# api/views/schools/education_level_viewsets.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers.schools.education_level_serializers import EducationalLevelSerializer
from schools.models.levels import EducationalLevel


class EducationalLevelViewSet(viewsets.ModelViewSet):
    queryset = EducationalLevel.objects.filter(is_active=True).order_by("order", "level_name")
    serializer_class = EducationalLevelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['level_name', 'description', 'color']
    ordering_fields = ['created_date', 'level_name', 'color', 'order']
    lookup_field = "uuid"
    permission_classes = [IsAuthenticatedOrReadOnly]