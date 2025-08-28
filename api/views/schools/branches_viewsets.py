from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from django.apps import apps

from api.serializers.schools.branch_serializers import SchoolBranchSerializer
from schools.models.school import SchoolBranch

class SchoolBranchViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranch.objects.all()
    serializer_class = SchoolBranchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['created_at']
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly]