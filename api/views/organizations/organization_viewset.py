# api/views/organizations/organization_viewset.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.serializers.organizations.organization_serializers import OrganizationSerializer
from organization.models.base import Organization

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    Authentication is handled by JWTSessionMiddleware which reads tokens from HttpOnly cookies.
    """
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = "uuid"

    # No explicit authentication_classes needed - JWTSessionMiddleware handles cookie-based auth
    permission_classes = [IsAuthenticatedOrReadOnly]
