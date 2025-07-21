"""
 project/api/schools_api.py 
 Handler for School API
"""
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action

from schools.models.schoolsModel import School, SchoolType
from api.serializers.schools.base import SchoolSerializer, SchoolTypeSerializer


class SchoolAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('q', '')
        schools = School.objects.all()
        if search_query:
            schools = schools.filter(name__icontains=search_query)
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)


class SchoolViewSet(viewsets.ViewSet):
    """
    ViewSet for handling CRUD operations for School, with filtering, search, and ordering.
    """
    permission_classes = [IsAuthenticated]
    # lookup_field = 'uuid'

    def list(self, request):
        queryset = School.objects.all()

        create_date = request.query_params.get("create_date", None)
        if create_date:
            queryset = queryset.filter(created_date=create_date)

        type_id = request.query_params.get("type", None)
        if type_id:
            queryset = queryset.filter(type__id=type_id)

        search = request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) |
                                       Q(local_name__icontains=search) |
                                       Q(president__icontains=search) |
                                       Q(founder__icontains=search))

        ordering = request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('created_date')

        if not queryset:
            return Response([], status=status.HTTP_200_OK)
         
        serializer = SchoolSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            school = School.objects.get(pk=pk)
            serializer = SchoolSerializer(school)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            school = School.objects.get(pk=pk)
            serializer = SchoolSerializer(school, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            school = School.objects.get(pk=pk)
            serializer = SchoolSerializer(
                school, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except School.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            school = School.objects.get(pk=pk)
            school.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except School.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, pk=None):
        """
        Returns analytics for a school, including counts of branches, degree offerings, major offerings, custom buttons, platform profiles, scholarships, and college associations.
        """
        try:
            school = School.objects.get(pk=pk)
            total_branches = school.school_branch.count() if hasattr(school, 'school_branch') else 0
            total_degree_offerings = school.degree_offerings.count() if hasattr(school, 'degree_offerings') else 0
            total_major_offerings = school.major_offerings.count() if hasattr(school, 'major_offerings') else 0
            total_custom_buttons = school.custom_buttons.count() if hasattr(school, 'custom_buttons') else 0
            total_platform_profiles = school.platform_profiles_school.count() if hasattr(school, 'platform_profiles_school') else 0
            # SchoolScholarship is not a related_name, so we query directly
            from schools.models.schoolsModel import SchoolScholarship
            total_scholarships = SchoolScholarship.objects.filter(school=school).count()
            total_college_associations = school.college_associations.count() if hasattr(school, 'college_associations') else 0
            data = {
                "total_branches": total_branches,
                "total_degree_offerings": total_degree_offerings,
                "total_major_offerings": total_major_offerings,
                "total_custom_buttons": total_custom_buttons,
                "total_platform_profiles": total_platform_profiles,
                "total_scholarships": total_scholarships,
                "total_college_associations": total_college_associations,
            }
            return Response(data, status=status.HTTP_200_OK)
        except School.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
