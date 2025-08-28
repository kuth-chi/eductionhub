# api/views/organizations/organization_viewset.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers.organizations.organization_serializers import OrganizationSerializer
from organization.models.base import Organization

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    """
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = "uuid"

    # Correct usage:
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticatedOrReadOnly]
