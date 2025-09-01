import base64
import json

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers.custom_jwt import CustomJWTSerializer
from api.views.auth.auth_viewset import set_auth_cookies
from user.models.profile import Profile

WEB_CLIENT_URL = settings.WEB_CLIENT_URL if hasattr(
    settings, 'WEB_CLIENT_URL') else "http://localhost:3000"


@login_required
def social_login_callback(request):
    """
    Handle social login callback and redirect to frontend with JWT tokens
    """
    try:
        user = request.user

        # Use the custom JWT serializer to create tokens with all user data
        jwt_serializer = CustomJWTSerializer()
        refresh = RefreshToken.for_user(user)
        access_token = jwt_serializer.get_token(user)

        # Get or create profile
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                "occupation": "untitled",
                "timezone": "UTC",
            },
        )

        # Prepare response data; includes tokens so the frontend can set its own HttpOnly cookies
        # Note: Tokens are also set as HttpOnly cookies on the backend domain via set_auth_cookies
        auth_data = {
            "status": "ok",
            "refresh": str(refresh),
            "access": str(access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
            "profile": {
                "uuid": str(profile.uuid),
                "photo": profile.photo.url if profile.photo else None,
                "gender": profile.gender,
                "occupation": profile.occupation,
                "timezone": profile.timezone,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "permissions": list(user.get_all_permissions()),
            "roles": [group.name for group in user.groups.all()],
            "social_accounts": [
                {
                    "provider": sa.provider,
                    "uid": sa.uid,
                    "extra_data": sa.extra_data,
                }
                # type: ignore[attr-defined]  # pylint: disable=no-member
                for sa in SocialAccount.objects.filter(user=user)
            ],
        }

        # Encode auth data for URL parameter
        auth_data_encoded = base64.b64encode(
            json.dumps(auth_data).encode()
        ).decode()

        # Get the frontend redirect URL from query parameters
        frontend_url = request.GET.get(
            "redirect_uri", f"{settings.WEB_CLIENT_URL}/auth/callback"
        )

        # Build redirect response
        separator = "&" if "?" in frontend_url else "?"
        redirect_url = f"{frontend_url}{separator}auth_data={auth_data_encoded}"

        # Set secure cookies on the redirect response
        response = redirect(redirect_url)
        response = set_auth_cookies(response, str(access_token), str(refresh))
        return response

    except Exception as e:  # pylint: disable=broad-except
        # Redirect to frontend with generic error; avoid leaking details
        import logging

        logging.getLogger(__name__).exception("Social login callback failed")

        frontend_url = request.GET.get(
            "redirect_uri", f"{settings.WEB_CLIENT_URL}/auth/callback"
        )
        separator = "&" if "?" in frontend_url else "?"
        error_param = "error=social_login_failed"
        # Optionally append detail in DEBUG for troubleshooting
        if getattr(settings, "DEBUG", False):
            from urllib.parse import quote

            error_param += f"&detail={quote(str(e))}"
        error_url = f"{frontend_url}{separator}{error_param}"
        return redirect(error_url)


@login_required
def social_login_status(request):
    """
    Check if user is authenticated via social login and return user info
    """
    try:
        user = request.user
        profile = Profile.objects.get(user=user)

        # Get social accounts
        # type: ignore[attr-defined]  # pylint: disable=no-member
        social_accounts_qs = SocialAccount.objects.filter(user=user)

        data = {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "profile": {
                "id": str(profile.uuid),
                "photo": profile.photo.url if profile.photo else None,
                "gender": profile.gender,
                "occupation": profile.occupation,
                "timezone": profile.timezone,
            },
            "social_accounts": [
                {
                    "provider": sa.provider,
                    "uid": sa.uid,
                    "extra_data": sa.extra_data,
                }
                for sa in social_accounts_qs
            ],
            "permissions": list(user.get_all_permissions()),
            "roles": [group.name for group in user.groups.all()],
        }
        return JsonResponse(data)

    except ObjectDoesNotExist:
        return JsonResponse({"authenticated": True, "profile": None})
    except Exception as e:  # pylint: disable=broad-except
        import logging

        logging.getLogger(__name__).exception(
            "Social login status check failed")
        payload = {"authenticated": False,
                   "error": "Unable to fetch social login status"}
        if getattr(settings, "DEBUG", False):
            payload["detail"] = str(e)
        return JsonResponse(payload, status=401)
