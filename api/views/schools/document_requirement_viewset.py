# api/views/schools/document_requirement_viewset.py
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from api.serializers.schools.document_requirement_serializers import (
    CreateDocumentRequirementSerializer, DocumentRequirementSerializer,
    MajorForDocumentRequirementSerializer, UpdateDocumentRequirementSerializer)
from schools.models.levels import DocumentRequirement, Major
from schools.models.school import School


class MajorDocumentRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document requirements.
    Supports CRUD operations and filtering by major.
    """

    queryset = DocumentRequirement.objects.filter(
        is_deleted=False).select_related('major')
    serializer_class = DocumentRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['major__uuid', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description', 'major__name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CreateDocumentRequirementSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateDocumentRequirementSerializer
        return DocumentRequirementSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_deleted = True
        instance.save()

    @action(detail=False, methods=['get'], url_path='by-major/(?P<major_uuid>[^/.]+)')
    def by_major(self, request, major_uuid=None):
        """Get all document requirements for a specific major"""
        try:
            major = Major.objects.get(uuid=major_uuid)
            requirements = self.queryset.filter(major=major)
            serializer = self.get_serializer(requirements, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Major not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def mandatory(self, request):
        """Get all mandatory document requirements"""
        requirements = self.queryset.filter(is_mandatory=True)
        serializer = self.get_serializer(requirements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def optional(self, request):
        """Get all optional document requirements"""
        requirements = self.queryset.filter(is_mandatory=False)
        serializer = self.get_serializer(requirements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='majors-by-school/(?P<school_uuid>[^/.]+)')
    def majors_by_school(self, request, school_uuid=None):
        """Get all majors available for a specific school"""
        try:
            school = School.objects.get(uuid=school_uuid)

            # Get majors associated with this school through colleges and branches
            majors = Major.objects.filter(
                colleges__branches__school=school,
                is_active=True,
                is_deleted=False
            ).distinct()

            serializer = MajorForDocumentRequirementSerializer(
                majors, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {"error": "School not found"},
                status=status.HTTP_404_NOT_FOUND
            )
