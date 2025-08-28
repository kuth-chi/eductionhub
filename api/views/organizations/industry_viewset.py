# api/views/organizations/industry_viewset.py
from rest_framework import viewsets

from api.serializers.organizations.industry_serializers import IndustrySerializer
from organization.models.base import Industry
    
class IndustryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing industries.
    """
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer