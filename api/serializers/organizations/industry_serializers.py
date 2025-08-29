# api/serializers/organizations/industry_serializers.py
from rest_framework import serializers

from organization.models.base import Industry

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'is_active', 'self_data']
        read_only_fields = ['created_at', 'updated_at']

