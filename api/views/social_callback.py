from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from user.models.profile import Profile
from allauth.socialaccount.models import SocialAccount
import json


@login_required
def social_login_callback(request):
    """
    Handle social login callback and redirect to frontend with JWT tokens
    """
    try:
        user = request.user

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add user_id for middleware authentication
        access_token["user_id"] = user.id

        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "",
            },
        )

        # Add custom claims to access token
        access_token["profile"] = {
            "id": str(profile.uuid),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "photo": profile.photo.url if profile.photo else None,
        }
        access_token["permissions"] = list(user.get_all_permissions())
        access_token["roles"] = [group.name for group in user.groups.all()]

        # Get social accounts
        social_accounts = SocialAccount.objects.filter(user=user)
        access_token["social_accounts"] = [
            {"provider": sa.provider, "uid": sa.uid, "extra_data": sa.extra_data}
            for sa in social_accounts
        ]

        # Prepare response data
        auth_data = {
            "refresh": str(refresh),
            "access": str(access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "profile": {
                "id": str(profile.uuid),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "email": profile.email,
                "photo": profile.photo.url if profile.photo else None,
            },
        }

        # Encode auth data for URL parameter
        import base64

        auth_data_encoded = base64.b64encode(json.dumps(auth_data).encode()).decode()

        # Redirect to frontend with auth data
        frontend_url = request.GET.get("redirect_uri", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/callback?auth_data={auth_data_encoded}"

        return redirect(redirect_url)

    except Exception as e:
        # Return error response
        return JsonResponse(
            {"error": str(e), "message": "Social login failed"}, status=500
        )


@login_required
def social_login_status(request):
    """
    Check if user is authenticated via social login and return user info
    """
    try:
        user = request.user
        profile = Profile.objects.get(user=user)

        # Get social accounts
        social_accounts = SocialAccount.objects.filter(user=user)

        return JsonResponse(
            {
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
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "email": profile.email,
                    "photo": profile.photo.url if profile.photo else None,
                },
                "social_accounts": [
                    {
                        "provider": sa.provider,
                        "uid": sa.uid,
                        "extra_data": sa.extra_data,
                    }
                    for sa in social_accounts
                ],
                "permissions": list(user.get_all_permissions()),
                "roles": [group.name for group in user.groups.all()],
            }
        )

    except Profile.DoesNotExist:
        return JsonResponse({"authenticated": True, "profile": None})
    except Exception as e:
        return JsonResponse({"authenticated": False, "error": str(e)}, status=401)
