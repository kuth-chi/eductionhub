# api/views/schools/qualification_candidate_viewset.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers.schools.candidate_qualification_serializers import \
    CandidateQualificationSerializer
from schools.models.levels import CandidateQualification


class QualificationCandidateViewSet(viewsets.ModelViewSet):
    queryset = CandidateQualification.objects.filter(is_deleted=False).select_related(
        'major', 'required_degree'
    ).prefetch_related(
        'major__colleges',
        'major__degrees'
    )
    serializer_class = CandidateQualificationSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]

    # Updated filter fields to match the actual model
    filterset_fields = {
        'major__uuid': ['exact'],
        'required_degree__uuid': ['exact'],
        'min_gpa': ['gte', 'lte', 'exact'],
        'min_english_score': ['gte', 'lte', 'exact'],
        'age_range': ['exact', 'icontains'],
        'is_active': ['exact'],
    }

    # Updated search fields to match actual model fields
    search_fields = ['qualifications', 'age_range', 'major__name',
                     'major__code', 'required_degree__degree_name']

    # Updated ordering fields to match actual model fields
    ordering_fields = ['created_at', 'updated_at',
                       'min_gpa', 'min_english_score']
    ordering = ['-created_at']

    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Override queryset to handle additional filtering logic
        """
        queryset = super().get_queryset()

        # Handle major schools filtering (for multi-school queries)
        major_schools_uuid = self.request.query_params.get(
            'major__schools__uuid', None)
        if major_schools_uuid:
            queryset = queryset.filter(
                major__colleges__school__uuid=major_schools_uuid)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create candidate qualifications
        """
        qualifications_data = request.data.get('qualifications', [])

        if not qualifications_data:
            return Response(
                {'error': 'No qualifications data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=qualifications_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about candidate qualifications
        """
        queryset = self.filter_queryset(self.get_queryset())

        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'with_gpa_requirement': queryset.exclude(min_gpa__isnull=True).count(),
            'with_english_requirement': queryset.exclude(min_english_score__isnull=True).count(),
            'with_age_requirement': queryset.exclude(age_range__exact='').count(),
            'with_subject_requirements': queryset.exclude(required_subjects__isnull=True).count(),
        }

        return Response(stats)
