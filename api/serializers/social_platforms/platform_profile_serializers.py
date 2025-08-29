# api/serializers/social_platforms/platform_profile_serializers.py

from rest_framework import serializers
from schools.models.online_profile import PlatformProfile

class PlatformProfileSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    platform_name = serializers.CharField(source="platform.name", read_only=True)

    class Meta:
        model = PlatformProfile
        fields = [
            "id",
            "uuid",
            "school",
            "school_name",
            "platform",
            "platform_name",
            "profile_url",
            "username",
            "is_active",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "uuid", "created_date", "updated_date"]