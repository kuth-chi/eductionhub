from django.apps import apps
from django_filters import BooleanFilter, CharFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (DjangoModelPermissionsOrAnonReadOnly,
                                        IsAdminUser, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers.schools.branch_serializers import SchoolBranchSerializer
from schools.models.school import SchoolBranch


class IsStaffOrSuperuserOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow staff or superuser to create/update/delete school branches.
    Regular authenticated users can only read.
    """

    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated

        # For write operations, require staff or superuser
        return (request.user and
                request.user.is_authenticated and
                (request.user.is_staff or request.user.is_superuser))


class SchoolBranchFilter(FilterSet):
    """Custom filter for SchoolBranch queryset"""
    school = CharFilter(field_name='school__uuid',
                        help_text="Filter by school UUID")
    school_id = CharFilter(field_name='school__uuid',
                           help_text="Filter by school UUID (alias for school)")
    school__uuid = CharFilter(
        field_name='school__uuid', help_text="Filter by school UUID")
    is_headquarters = BooleanFilter(field_name='is_headquarters')
    is_active = BooleanFilter(field_name='is_active')
    country = CharFilter(field_name='country__id')
    state = CharFilter(field_name='state__id')
    city = CharFilter(field_name='city__id')
    village = CharFilter(field_name='village__id')

    class Meta:
        model = SchoolBranch
        fields = [
            'school', 'school_id', 'school__uuid', 'is_headquarters', 'is_active',
            'country', 'state', 'city', 'village'
        ]


class SchoolBranchViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranch.objects.select_related(
        'school', 'country', 'state', 'city', 'village'
    ).prefetch_related('colleges', 'degrees_offered', 'majors_offered')
    serializer_class = SchoolBranchSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SchoolBranchFilter
    search_fields = ['name', 'short_name', 'address', 'location']
    ordering_fields = ['created_at', 'name', 'is_headquarters']
    # Default ordering: headquarters first, then by name
    ordering = ['-is_headquarters', 'name']
    lookup_field = 'uuid'
    permission_classes = [IsStaffOrSuperuserOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Override get_queryset to ensure proper filtering by school relationship
        """
        queryset = super().get_queryset()

        # Get school filter parameters
        school_id = self.request.query_params.get('school_id')
        school_uuid = self.request.query_params.get('school__uuid')
        school_param = self.request.query_params.get('school')

        # Apply school filtering if any school parameter is provided
        if school_id:
            queryset = queryset.filter(school__uuid=school_id)
        elif school_uuid:
            queryset = queryset.filter(school__uuid=school_uuid)
        elif school_param:
            queryset = queryset.filter(school__uuid=school_param)

        return queryset

    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling and permission check"""
        # Additional permission check
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'You must be a staff member or administrator to create school branches.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': f'Failed to create school branch: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Override destroy to provide better permission check"""
        # Additional permission check
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'You must be a staff member or administrator to delete school branches.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Override update to provide better permission check"""
        # Additional permission check for updates
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'You must be a staff member or administrator to update school branches.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)
