from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (DjangoModelPermissionsOrAnonReadOnly,
                                        IsAuthenticatedOrReadOnly)

from api.serializers.schools.branch_serializers import SchoolBranchSerializer
from schools.models.school import SchoolBranch


class SchoolBranchViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranch.objects.all()
    serializer_class = SchoolBranchSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school__uuid',
                        'is_headquarters', 'is_active']
    search_fields = ['name', 'short_name', 'address', 'location']
    ordering_fields = ['created_at', 'name', 'established_year']
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Filter branches based on query parameters
        """
        queryset = SchoolBranch.objects.select_related(
            'school', 'city', 'state', 'country', 'village'
        ).prefetch_related('degrees_offered', 'majors_offered')

        # Filter by school ID (UUID)
        school_param = self.request.query_params.get('school', None)

        if school_param:
            # Handle both school ID and school UUID
            import uuid
            try:
                # Validate if it's a valid UUID
                uuid.UUID(school_param)
                # Try to filter by school UUID first
                queryset = queryset.filter(school__uuid=school_param)
            except ValueError:
                # Fall back to filtering by school ID if not a valid UUID
                try:
                    queryset = queryset.filter(school_id=school_param)
                except Exception as e:
                    # If all fails, return empty queryset
                    queryset = queryset.none()

        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by headquarters status
        is_headquarters = self.request.query_params.get(
            'is_headquarters', None)
        if is_headquarters is not None:
            queryset = queryset.filter(
                is_headquarters=is_headquarters.lower() == 'true')

        # Exclude deleted branches by default
        if not self.request.query_params.get('include_deleted', False):
            queryset = queryset.filter(is_deleted=False)

        return queryset
