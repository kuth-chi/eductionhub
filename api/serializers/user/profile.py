from rest_framework import serializers
from user.models.profile import Profile
from user.models.base import User


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "uuid",
            "user",
            "photo",
            "gender",
            "occupation",
            "timezone",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ("uuid", "created_date", "updated_date", "user")
