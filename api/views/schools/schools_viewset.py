"""
 project/api/schools_api.py 
 Handler for School API
"""
import logging
from typing import Any, Dict

from django.db.models import Count, Q
from django.http import Http404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.schools.base import (SchoolListSerializer,
                                          SchoolSerializer,
                                          SchoolTypeSerializer)
from api.serializers.schools.branch_serializers import SchoolBranchSerializer
# Import our custom permissions
from rbac.permissions import SchoolManagementPermission
from schools.models.levels import (SchoolCollegeAssociation,
                                   SchoolDegreeOffering, SchoolMajorOffering)
from schools.models.online_profile import PlatformProfile
from schools.models.school import (School, SchoolBranch, SchoolCustomizeButton,
                                   SchoolScholarship)

logger = logging.getLogger(__name__)


class SchoolAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *_args, **_kwargs):
        search_query = request.query_params.get("q", "")
        schools = School.objects.all()  # pylint: disable=no-member
        if search_query:
            schools = schools.filter(name__icontains=search_query)
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)


class CustomSchoolPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()  # pylint: disable=no-member
    # serializer_class = SchoolSerializer
    lookup_field = "uuid"
    pagination_class = CustomSchoolPagination
    # Accept both multipart (for file uploads) and JSON bodies for updates
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['name', 'local_name', 'established',
                       'created_date', 'updated_date', 'slug', 'uuid']
    search_fields = ['name', 'local_name', 'description']

    def get_queryset(self):
        queryset = School.objects.all()  # pylint: disable=no-member

        # Safely check if the action exists and is "list"
        if getattr(self, 'action', None) == "list":
            # Annotate with unique counts of related branches, colleges, majors, and degrees
            return queryset.annotate(
                branch_count=Count('school_branches', distinct=True),
                college_count=Count(
                    'college_associations__college', distinct=True),
                major_count=Count('major_offerings__major', distinct=True),
                degree_count=Count('degree_offerings__degree', distinct=True),
            )

        return queryset

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == "list":
            return SchoolListSerializer
        return SchoolSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ["list", "retrieve", "analytics", "branches"]:
            # Public read access for these actions
            return [AllowAny()]
        else:
            # Use role-based permissions for create, update, delete
            return [SchoolManagementPermission()]

    def list(self, request, *args, **kwargs):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance_id = None
        try:
            instance = self.get_object()
            instance_id = getattr(instance, "uuid", None)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error updating school %s: %s", instance_id, e)
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, *args, **kwargs):
        instance_id = None
        try:
            instance = self.get_object()
            instance_id = getattr(instance, "uuid", None)
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error partially updating school %s: %s", instance_id, e)
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, _request, **kwargs):
        try:
            lookup_kwarg_name = getattr(self, "lookup_url_kwarg", None) or getattr(
                self, "lookup_field", "pk")
            identifier = kwargs.get(lookup_kwarg_name)
            # Since lookup_field is 'uuid', identifier is the uuid value
            school = School.objects.get(
                uuid=identifier)  # pylint: disable=no-member

            data: Dict[str, Any] = {
                "total_branches": SchoolBranch.objects.filter(school=school).count(),  # pylint: disable=no-member
                "total_degree_offerings": SchoolDegreeOffering.objects.filter(school_id=school.pk).count(),  # pylint: disable=no-member
                "total_major_offerings": SchoolMajorOffering.objects.filter(school=school).count(),  # pylint: disable=no-member
                "total_custom_buttons": SchoolCustomizeButton.objects.filter(school=school).count(),  # pylint: disable=no-member
                "total_platform_profiles": PlatformProfile.objects.filter(school=school).count(),  # pylint: disable=no-member
                "total_scholarships": SchoolScholarship.objects.filter(school=school).count(),  # pylint: disable=no-member
                "total_college_associations": SchoolCollegeAssociation.objects.filter(school=school).count(),  # pylint: disable=no-member
            }

            if school.type.exists():
                data["school_types"] = SchoolTypeSerializer(
                    school.type.all(), many=True).data
            else:
                data["school_types"] = []

            return Response(data, status=status.HTTP_200_OK)

        except School.DoesNotExist:  # pylint: disable=no-member
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error retrieving analytics for school %s: %s", identifier, e)
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="branches")
    def branches(self, _request, **kwargs):
        """Get all branches for a specific school."""
        try:
            lookup_kwarg_name = getattr(self, "lookup_url_kwarg", None) or getattr(
                self, "lookup_field", "pk")
            identifier = kwargs.get(lookup_kwarg_name)
            # Since lookup_field is 'uuid', identifier is the uuid value
            school = School.objects.get(
                uuid=identifier)  # pylint: disable=no-member

            # Get all branches for this school
            branches = SchoolBranch.objects.filter(school=school).order_by(
                'created_at')  # pylint: disable=no-member

            # Apply pagination if needed
            page = self.paginate_queryset(branches)
            if page is not None:
                serializer = SchoolBranchSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = SchoolBranchSerializer(branches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except School.DoesNotExist:  # pylint: disable=no-member
            return Response({"detail": "School not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error retrieving branches for school %s: %s", identifier, e)
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
