# api/organizations/organization_viewsets.py

from rest_framework import serializers
from api.serializers.organizations.founder_serializers import FounderSerializer
from api.serializers.organizations.industry_serializers import IndustrySerializer
from organization.models.base import Industry, Organization, Founder


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for the Organization model."""
    industries = IndustrySerializer(many=True, read_only=True)
    industry_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Industry.objects.all(), source='industries', write_only=True, allow_null=True, required=False)

    founders = FounderSerializer(many=True, read_only=True)
    founder_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Founder.objects.all(), source='founders', write_only=True, required=False)

    logo = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        """Meta options for the OrganizationSerializer."""
        model = Organization
        fields = [
            'uuid',
            'slug',
            'logo',
            'name',
            'local_name',
            'description',
            'established_year',
            'primary_color',
            'on_primary_color',
            'created_at',
            'updated_at',
            'is_active',
            'self_data',
            'founders',
            'founder_ids',
            'industries',
            'industry_ids',
        ]
        read_only_fields = ['uuid', 'slug', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Customize the representation to return logo path."""
        data = super().to_representation(instance)
        if instance.logo:
            data['logo'] = instance.logo.name if hasattr(instance.logo, 'name') else str(instance.logo)
        else:
            data['logo'] = None
        return data

    def create(self, validated_data):
        industries = validated_data.pop('industries', [])
        founders = validated_data.pop('founders', [])
        organization = Organization.objects.create(**validated_data)
        if industries:
            organization.industries.set(industries)
        if founders:
            organization.founders.set(founders)
        return organization

    def update(self, instance, validated_data):
        industries = validated_data.pop('industries', None)
        founders = validated_data.pop('founders', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if industries is not None:
            instance.industries.set(industries)

        if founders is not None:
            instance.founders.set(founders)

        instance.save()
        return instance


