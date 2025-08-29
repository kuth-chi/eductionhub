# api/serializers/social_platform/platform_serializers.py

from rest_framework import serializers
from schools.models.online_profile import Platform


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = [
            "id",
            "uuid",
            "name",
            "short_name",
            "url",
            "icon",
            "self_data",
            "is_active",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "uuid", "created_date", "updated_date"]