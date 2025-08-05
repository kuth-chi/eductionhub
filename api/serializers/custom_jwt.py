from datetime import datetime
from typing import Any, Dict, Optional
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from user.models.profile import Profile
from allauth.socialaccount.models import SocialAccount

def sanitize_extra_data(data):
    """Recursively convert datetime objects to ISO strings for JWT compatibility."""
    if isinstance(data, dict):
        return {k: sanitize_extra_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_extra_data(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = str(user.pk)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user is None:
            raise serializers.ValidationError("User authentication failed.")

        request = self.context.get("request", None)

        # Issue tokens
        access_token = self.get_token(self.user)
        refresh_token = RefreshToken.for_user(self.user)

        # Get or create user profile
        profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                "first_name": self.user.first_name or "",
                "last_name": self.user.last_name or "",
                "email": self.user.email or "",
            },
        )

        profile_data = {
            "id": str(profile.uuid),
            "first_name": profile.user.first_name,
            "last_name": profile.user.last_name,
            "email": profile.user.email,
            "last_login": profile.user.last_login.isoformat() if profile.user.last_login else None,
            "is_active": profile.user.is_active,
            "photo": profile.photo.url if profile.photo else None,
        }

        # Inject custom claims into both tokens
        common_claims = {
            "profile": profile_data,
            "permissions": list(self.user.get_all_permissions()),
            "roles": [g.name for g in self.user.groups.all()],
            "social_accounts": [
                {
                    "provider": sa.provider,
                    "uid": sa.uid,
                    "extra_data": sanitize_extra_data(sa.extra_data),
                }
                for sa in SocialAccount.objects.filter(user=self.user)
            ],
        }


        for token in [access_token, refresh_token]:
            for key, value in common_claims.items():
                token[key] = value

        # Add user-agent and full IP
        if request:
            token_ip = request.META.get("REMOTE_ADDR", "")
            token_ua = request.META.get("HTTP_USER_AGENT", "")
            access_token["ip"] = token_ip
            access_token["ua"] = token_ua
            refresh_token["ip"] = token_ip
            refresh_token["ua"] = token_ua

        # Return string versions of the tokens
        data["access"] = str(access_token)
        data["refresh"] = str(refresh_token)

        return data
