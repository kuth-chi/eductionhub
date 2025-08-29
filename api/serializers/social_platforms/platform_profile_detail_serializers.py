# api/serializers/platform_profile_detail_serializers.py

from rest_framework import serializers
from api.serializers.schools.base import PlatformSerializer
from schools.models.online_profile import PlatformProfile

class PlatformProfileDetailSerializer(serializers.ModelSerializer):
    school = serializers.StringRelatedField()
    platform = PlatformSerializer()

    class Meta:
        model = PlatformProfile
        fields = [
            "uuid",
            "school",
            "platform",
            "profile_url",
            "username",
            "is_active",
            "created_date",
            "updated_date",
        ]