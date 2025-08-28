"""Major ViewSet with flexible filtering.

Supports query params:
- school: numeric ID or UUID of School; filters majors linked via colleges->branches->school
- branch: numeric ID or UUID of SchoolBranch; filters majors linked via colleges->that branch
- college: numeric ID or UUID of College
- degree: numeric ID or UUID of EducationDegree
- is_active: 'true'/'false' to filter by active status
"""

from uuid import UUID

from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers.schools.major_serializers import MajorSerializer
from schools.models.levels import Major


class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        # Optional: exclude deleted by default if model has is_deleted
        if hasattr(Major, 'is_deleted'):
            qs = qs.filter(Q(is_deleted=False) | Q(is_deleted__isnull=True))

        params = self.request.query_params

        # Filter by is_active=true/false
        is_active = params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ('true', '1', 'yes'):
                qs = qs.filter(is_active=True)
            elif is_active.lower() in ('false', '0', 'no'):
                qs = qs.filter(is_active=False)

        # Filter by school (via colleges -> branches -> school)
        school = params.get('school')
        if school:
            school_q = Q()
            if school.isdigit():
                school_q |= Q(colleges__branches__school__id=int(school))
            else:
                try:
                    UUID(str(school))
                    school_q |= Q(colleges__branches__school__uuid=str(school))
                except Exception:
                    pass
            qs = qs.filter(school_q)

        # Filter by college (supports multiple values)
        colleges = params.getlist('college') or ([] if params.get(
            'college') is None else [params.get('college')])
        if colleges:
            college_q = Q()
            for college in colleges:
                if college is None:
                    continue
                if college.isdigit():
                    college_q |= Q(colleges__id=int(college))
                else:
                    try:
                        UUID(str(college))
                        college_q |= Q(colleges__uuid=str(college))
                    except Exception:
                        pass
            qs = qs.filter(college_q)

        # Filter by specific branch (via colleges -> branches)
        branches = params.getlist('branch') or (
            [] if params.get('branch') is None else [params.get('branch')])
        if branches:
            branch_q = Q()
            for branch in branches:
                if branch is None:
                    continue
                if branch.isdigit():
                    branch_q |= Q(colleges__branches__id=int(branch))
                else:
                    try:
                        UUID(str(branch))
                        branch_q |= Q(colleges__branches__uuid=str(branch))
                    except Exception:
                        pass
            qs = qs.filter(branch_q)

        # Filter by degree
        degree = params.get('degree')
        if degree:
            degree_q = Q()
            if degree.isdigit():
                degree_q |= Q(degrees__id=int(degree))
            else:
                try:
                    UUID(str(degree))
                    degree_q |= Q(degrees__uuid=str(degree))
                except Exception:
                    pass
            qs = qs.filter(degree_q)

        return qs.distinct()
