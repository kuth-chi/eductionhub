"""
Complete social authentication views with dj-rest-auth integration
"""

import logging

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.facebook.views import \
    FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.telegram.views import TelegramProvider
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.models.profile import Profile

logger = logging.getLogger(__name__)


class GoogleSocialLoginView(SocialLoginView):
    """Google OAuth2 social login view using dj-rest-auth"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = f"{settings.BACKEND_URL}/accounts/google/login/callback/"
    client_class = OAuth2Client
    permission_classes = [AllowAny]

    def get_response(self):
        """Override to return custom JWT tokens with profile data"""
        try:
            # Get the default response from parent
            response = super().get_response()

            # Generate JWT tokens for the authenticated user
            user = self.user
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Get or create profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "occupation": "untitled",
                    "timezone": "UTC",
                },
            )

            # Prepare enhanced response data
            profile_data = {
                "id": str(profile.uuid),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "photo": profile.photo.url if profile.photo else None,
                "gender": profile.gender,
                "occupation": profile.occupation,
                "timezone": profile.timezone,
                "is_active": user.is_active,
            }

            # Add profile and permissions to tokens
            for token in [refresh, access]:
                token["profile"] = profile_data
                token["permissions"] = list(user.get_all_permissions())
                token["roles"] = [group.name for group in user.groups.all()]
                token["social_accounts"] = [
                    {"provider": sa.provider, "uid": sa.uid,
                        "extra_data": sa.extra_data}
                    for sa in SocialAccount.objects.filter(user=user)
                ]

            # Custom response data
            custom_data = {
                "access": str(access),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
                "profile": profile_data,
            }

            return Response(custom_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Google social login error: {str(e)}")
            return Response(
                {"error": "Google authentication failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FacebookSocialLoginView(SocialLoginView):
    """Facebook OAuth2 social login view using dj-rest-auth"""
    adapter_class = FacebookOAuth2Adapter
    permission_classes = [AllowAny]

    def get_response(self):
        """Override to return custom JWT tokens with profile data"""
        try:
            # Get the default response from parent
            response = super().get_response()

            # Generate JWT tokens for the authenticated user
            user = self.user
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Get or create profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "occupation": "untitled",
                    "timezone": "UTC",
                },
            )

            # Prepare enhanced response data
            profile_data = {
                "id": str(profile.uuid),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "photo": profile.photo.url if profile.photo else None,
                "gender": profile.gender,
                "occupation": profile.occupation,
                "timezone": profile.timezone,
                "is_active": user.is_active,
            }

            # Add profile and permissions to tokens
            for token in [refresh, access]:
                token["profile"] = profile_data
                token["permissions"] = list(user.get_all_permissions())
                token["roles"] = [group.name for group in user.groups.all()]
                token["social_accounts"] = [
                    {"provider": sa.provider, "uid": sa.uid,
                        "extra_data": sa.extra_data}
                    for sa in SocialAccount.objects.filter(user=user)
                ]

            # Custom response data
            custom_data = {
                "access": str(access),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
                "profile": profile_data,
            }

            return Response(custom_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Facebook social login error: {str(e)}")
            return Response(
                {"error": "Facebook authentication failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TelegramSocialLoginView(SocialLoginView):
    """Telegram social login view using dj-rest-auth"""
    adapter_class = TelegramProvider
    permission_classes = [AllowAny]

    def get_response(self):
        """Override to return custom JWT tokens with profile data"""
        try:
            # Get the default response from parent
            response = super().get_response()

            # Generate JWT tokens for the authenticated user
            user = self.user
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Get or create profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "occupation": "untitled",
                    "timezone": "UTC",
                },
            )

            # Prepare enhanced response data
            profile_data = {
                "id": str(profile.uuid),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "photo": profile.photo.url if profile.photo else None,
                "gender": profile.gender,
                "occupation": profile.occupation,
                "timezone": profile.timezone,
                "is_active": user.is_active,
            }

            # Add profile and permissions to tokens
            for token in [refresh, access]:
                token["profile"] = profile_data
                token["permissions"] = list(user.get_all_permissions())
                token["roles"] = [group.name for group in user.groups.all()]
                token["social_accounts"] = [
                    {"provider": sa.provider, "uid": sa.uid,
                        "extra_data": sa.extra_data}
                    for sa in SocialAccount.objects.filter(user=user)
                ]

            # Custom response data
            custom_data = {
                "access": str(access),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
                "profile": profile_data,
            }

            return Response(custom_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Telegram social login error: {str(e)}")
            return Response(
                {"error": "Telegram authentication failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
