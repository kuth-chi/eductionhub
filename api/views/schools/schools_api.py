"""
 project/api/schools_api.py 
 Handler for School API
"""
import logging
from typing import Dict, Any, List
from rest_framework.utils.serializer_helpers import ReturnList
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from schools.models.online_profile import PlatformProfile
from schools.models.school import School, SchoolBranch, SchoolCustomizeButton, SchoolScholarship, SchoolType
from schools.models.levels import (
    SchoolDegreeOffering,
    SchoolMajorOffering,
    SchoolCollegeAssociation,
)
from api.serializers.schools.base import SchoolListSerializer, SchoolSerializer, SchoolTypeSerializer

logger = logging.getLogger(__name__)

class SchoolAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get("q", "")
        schools = School.objects.all()
        if search_query:
            schools = schools.filter(name__icontains=search_query)
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

class CustomSchoolPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    # serializer_class = SchoolSerializer
    lookup_field = "uuid"
    pagination_class = CustomSchoolPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['name', 'local_name', 'established', 'created_date', 'updated_date', 'slug', 'uuid']
    search_fields = ['name', 'local_name', 'description']
    
    def get_queryset(self):
        queryset = School.objects.all()

        # Safely check if the action exists and is "list"
        if getattr(self, 'action', None) == "list":
            # Annotate with counts of related branches and colleges
            return queryset.annotate(
                branch_count=Count('school_branches', distinct=True),
                college_count=Count('school_branches__colleges', distinct=True)
            )

        return queryset

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == "list":
            return SchoolListSerializer
        return SchoolSerializer 

    def get_permissions(self):
        if self.action in ["list", "retrieve", "analytics"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        queryset = self.get_queryset()
        create_date = request.query_params.get("create_date")
        if create_date:
            queryset = queryset.filter(created_date__date=create_date)

        type_id = request.query_params.get("type")
        if type_id:
            queryset = queryset.filter(type__id=type_id)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(local_name__icontains=search)
                | Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering", "created_date")
        queryset = queryset.order_by(ordering)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, uuid=None):
        try:
            school = School.objects.get(uuid=uuid)
            serializer = self.get_serializer(school, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error updating school {uuid}: {e}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, uuid=None):
        try:
            school = School.objects.get(uuid=uuid)
            serializer = self.get_serializer(school, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error partially updating school {uuid}: {e}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, uuid=None):
        try:
            school = School.objects.get(uuid=uuid)

            data: Dict[str, Any] = {
                "total_branches": SchoolBranch.objects.filter(school=school).count(),
                "total_degree_offerings": SchoolDegreeOffering.objects.filter(school_id=school.pk).count(),
                "total_major_offerings": SchoolMajorOffering.objects.filter(school=school).count(),
                "total_custom_buttons": SchoolCustomizeButton.objects.filter(school=school).count(),
                "total_platform_profiles": PlatformProfile.objects.filter(school=school).count(),
                "total_scholarships": SchoolScholarship.objects.filter(school=school).count(),
                "total_college_associations": SchoolCollegeAssociation.objects.filter(school=school).count(),
            }

            if school.type.exists():
                data["school_types"] = SchoolTypeSerializer(school.type.all(), many=True).data
            else:
                data["school_types"] = []

            return Response(data, status=status.HTTP_200_OK)

        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error retrieving analytics for school {uuid}: {e}")
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

