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
