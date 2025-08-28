# api/views/schools/colleges_viewset.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny

from api.serializers.schools.college_serializers import CollegeSerializer
from rbac.permissions import CollegeManagementPermission
from schools.models.levels import College


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'established_year']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['name']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ["list", "retrieve"]:
            # Public read access for listing and retrieving colleges
            return [AllowAny()]
        else:
            # Use role-based permissions for create, update, delete
            return [CollegeManagementPermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        school_uuid = self.request.query_params.get('school', None)

        if school_uuid:
            queryset = queryset.filter(branches__school__uuid=school_uuid)

        return queryset.distinct()
