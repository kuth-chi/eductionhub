"""
Custom user details serializer for dj-rest-auth
"""

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models.profile import Profile

User = get_user_model()


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User details serializer for dj-rest-auth.
    Returns user info with profile and social accounts.
    """
    profile = serializers.SerializerMethodField()
    social_accounts = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'is_active', 'last_login',
            'profile', 'social_accounts', 'permissions', 'roles'
        ]
        read_only_fields = ['id', 'username',
                            'is_staff', 'is_superuser', 'last_login']

    def get_profile(self, obj):
        """Get user profile data"""
        try:
            profile = Profile.objects.get(user=obj)
            return {
                'id': str(profile.uuid),
                'first_name': obj.first_name,
                'last_name': obj.last_name,
                'email': obj.email,
                'photo': profile.photo.url if profile.photo else None,
                'gender': profile.gender,
                'occupation': profile.occupation,
                'timezone': profile.timezone,
                'last_login': obj.last_login.isoformat() if obj.last_login else None,
            }
        except Profile.DoesNotExist:
            return None

    def get_social_accounts(self, obj):
        """Get user's social accounts"""
        social_accounts = SocialAccount.objects.filter(user=obj)
        return [
            {
                'provider': sa.provider,
                'uid': sa.uid,
                'extra_data': sa.extra_data
            }
            for sa in social_accounts
        ]

    def get_permissions(self, obj):
        """Get user permissions"""
        return list(obj.get_all_permissions())

    def get_roles(self, obj):
        """Get user roles (groups)"""
        return [group.name for group in obj.groups.all()]
