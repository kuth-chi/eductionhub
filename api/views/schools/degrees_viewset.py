# api/views/schools/degrees_viewset.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.serializers.schools.degree_serializers import EducationDegreeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from schools.models.levels import EducationDegree


class EducationDegreeViewSet(viewsets.ModelViewSet):
    queryset = EducationDegree.objects.all()
    serializer_class = EducationDegreeSerializer
    lookup_field = "uuid"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'duration_years', 'level', 'credit_hours', 'color', 'degree_name']
    search_fields = ['name', 'description']
    ordering_fields = ['created_date', 'updated_date']
    ordering = ['degree_name', 'created_date']
    permission_classes = [IsAuthenticatedOrReadOnly]