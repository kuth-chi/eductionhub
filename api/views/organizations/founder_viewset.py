# api/views/organizations/founder_viewset.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers.organizations.founder_serializers import FounderSerializer
from organization.models.base import Founder
    

class FounderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing founders.
    """
    queryset = Founder.objects.all()
    serializer_class = FounderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "uuid"