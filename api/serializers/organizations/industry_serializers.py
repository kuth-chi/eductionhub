# api/serializers/organizations/industry_serializers.py
from rest_framework import serializers

from organization.models.base import Industry

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'uuid', 'name', 'slug', 'created_by', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['uuid', 'slug', 'created_at', 'updated_at']

