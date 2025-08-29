# api/serializers/organizations/founder_serializers.py
from rest_framework import serializers

from organization.models.base import Founder

class FounderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Founder
        fields = ['uuid', 'name', 'national_name']
        read_only_fields = ['created_at', 'updated_at']
