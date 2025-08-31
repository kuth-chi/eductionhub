"""
Custom registration serializer for dj-rest-auth
"""

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models.profile import Profile

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer that creates user profile automatically
    """
    first_name = serializers.CharField(
        max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(
        max_length=30, required=False, allow_blank=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        })
        return data

    def save(self, request):
        """Save user and create profile"""
        user = super().save(request)

        # Create user profile
        Profile.objects.get_or_create(
            user=user,
            defaults={
                'occupation': 'untitled',
                'timezone': 'UTC',
            }
        )

        return user
