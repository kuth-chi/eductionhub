# views/userauth.py

import jwt
import logging
from typing import cast
from user_agents import parse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.models import SocialAccount
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.models.profile import Profile
from api.serializers.custom_jwt import CustomTokenObtainPairSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import update_last_login

logger = logging.getLogger(__name__)


def set_auth_cookies(response, access, refresh):
    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=False,  # Set to False for local development
        samesite="Strict",
        path="/",
        max_age=5 * 60,
    )
    response.set_cookie(
        "refresh_token",
        refresh,
        httponly=True,
        secure=False,  # Set to False for local development
        samesite="Strict",
        path="/",
        max_age=7 * 24 * 3600,
    )
    return response


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user  # <-- get the authenticated user here
        update_last_login(None, user)  # update last login time

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        # Parse user agent & IP
        ua_string = request.META.get("HTTP_USER_AGENT", "")
        ip = get_client_ip(request)
        user_agent = parse(ua_string)

        device_name = f"{user_agent.device.brand or ''} {user_agent.device.model or ''}".strip() or "Unknown Device"
        os = f"{user_agent.os.family} {user_agent.os.version_string}".strip() or "Unknown OS"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip() or "Unknown Browser"

        profile = Profile.objects.get(user=user)
        profile_data = {
            "id": str(profile.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "photo": profile.photo.url if profile.photo else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        }

        # Add custom claims to tokens
        refresh_token = RefreshToken(refresh)
        access_token = refresh_token.access_token

        for token in [refresh_token, access_token]:
            token["profile"] = profile_data
            token["ua"] = ua_string
            token["ip"] = ip
            token["device_name"] = device_name
            token["os"] = os
            token["browser"] = browser

        response = super().post(request, *args, **kwargs)
        return set_auth_cookies(response, str(access_token), str(refresh_token))


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class SocialLoginJWTView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = request.user
            if not user or not user.is_authenticated:
                return Response(
                    {"error": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Embed profile data
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "email": user.email or "",

                },
            )

            profile_data = {
                "id": str(profile.uuid),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "last_login": profile.user.last_login.isoformat() if profile.user.last_login else None,
                "photo": profile.photo.url if profile.photo else None,
                "is_active": profile.user.is_active,
            }

            for token in [refresh, access]:
                token["profile"] = profile_data
                token["permissions"] = list(user.get_all_permissions())
                token["roles"] = [group.name for group in user.groups.all()]
                token["social_accounts"] = [
                    {
                        "provider": sa.provider,
                        "uid": sa.uid,
                        "extra_data": sa.extra_data,
                    }
                    for sa in SocialAccount.objects.filter(user=user)
                ]
                token["ua"] = request.META.get("HTTP_USER_AGENT", "")
                token["ip"] = request.META.get("REMOTE_ADDR", "")

            response = Response(
                {
                    "refresh": str(refresh),
                    "access": str(access),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                    "profile": profile_data,
                },
                status=status.HTTP_200_OK,
            )

            return set_auth_cookies(response, str(access), str(refresh))

        except Exception as e:
            logger.error(f"Social login failed: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        response = Response({"detail": "Logged out successfully"})
        try:
            for token in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=token)
        except:
            pass

        # Clear cookies
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.delete_cookie("csrftoken")

        if hasattr(request, "session"):
            request.session.flush()

        return response


class AuthStatusView(APIView):
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(user=request.user)
            social_accounts = SocialAccount.objects.filter(user=request.user)

            ua_string = request.META.get("HTTP_USER_AGENT", "")
            user_agent = parse(ua_string)

            device_info = {
                "device_family": user_agent.device.family,   # e.g. "iPhone"
                "device_brand": user_agent.device.brand,     # e.g. "Apple"
                "device_model": user_agent.device.model,     # e.g. "iPhone 12"
                "os_family": user_agent.os.family,            # e.g. "iOS"
                "os_version": user_agent.os.version_string,   # e.g. "14.4"
                "browser_family": user_agent.browser.family,  # e.g. "Mobile Safari"
                "browser_version": user_agent.browser.version_string,
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
                "is_pc": user_agent.is_pc,
            }

            return Response({
                "authenticated": True,
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "last_logged_in": request.user.last_login,
                },
                "profile": {
                    "id": str(profile.uuid),
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "email": profile.user.email,
                    "photo": profile.photo.url if profile.photo else None,
                },
                "social_accounts": [
                    {"provider": sa.provider, "uid": sa.uid, "extra_data": sa.extra_data}
                    for sa in social_accounts
                ],
                "permissions": list(request.user.get_all_permissions()),
                "roles": [group.name for group in request.user.groups.all()],
                "ua": ua_string,
                "device": device_info,
                "ip": request.META.get("REMOTE_ADDR", ""),
            })
        except Profile.DoesNotExist:
            return Response({"authenticated": True, "profile": None}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching auth status: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Token refresh requested from IP: {request.META.get('REMOTE_ADDR')}")
        try:
            data = cast(dict, request.data)
            if "refresh" not in data:
                cookie_refresh = request.COOKIES.get("refresh_token")
                if not cookie_refresh:
                    return Response(
                        {"error": "No refresh token provided in body or cookie"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                data["refresh"] = cookie_refresh
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200 and isinstance(response.data, dict):
                access = response.data.get("access")
                if access:
                    response = set_auth_cookies(response, access, data["refresh"])
            return response
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return Response(
                {"error": f"Token refresh failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        
class ActiveSessionsView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            logger.warning(f"No profile found for user {request.user.id}")
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        sessions = []

        # Get all outstanding (refresh) tokens for the user
        tokens = OutstandingToken.objects.filter(user=request.user)

        for token in tokens:
            try:
                # Decode the refresh token to extract custom claims (e.g., ua, ip)
                token_data = jwt.decode(
                    token.token,
                    settings.SIMPLE_JWT['SIGNING_KEY'],
                    algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                    options={"verify_exp": False},  # Do not fail if expired, we handle manually
                )
            except jwt.InvalidTokenError as e:
                logger.debug(f"Skipping invalid token {token.id}: {str(e)}")
                continue

            ua_string = token_data.get('ua', '')
            ip = token_data.get('ip', '')
            last_used = token.created_at.isoformat() if token.created_at else None

            # Parse user agent string safely
            if ua_string:
                try:
                    user_agent = parse(ua_string)
                    device_name = f"{user_agent.device.brand or ''} {user_agent.device.model or ''}".strip() or "Unknown Device"
                    os = f"{user_agent.os.family} {user_agent.os.version_string}".strip() or "Unknown OS"
                    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip() or "Unknown Browser"
                except Exception as e:
                    logger.error(f"Failed to parse user agent '{ua_string}': {str(e)}")
                    device_name, os, browser = "Unknown Device", "Unknown OS", "Unknown Browser"
            else:
                device_name, os, browser = "Unknown Device", "Unknown OS", "Unknown Browser"

            sessions.append({
                "sessionId": str(token.id),
                "profile": {
                    "id": str(profile.uuid),
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "email": profile.user.email,
                    "last_login": profile.user.last_login.isoformat() if profile.user.last_login else None,
                    "photo": profile.photo.url if profile.photo else None,
                },
                "permissions": list(request.user.get_all_permissions()),
                "roles": [group.name for group in request.user.groups.all()],
                "socialAccounts": [
                    {
                        "provider": sa.provider,
                        "uid": sa.uid,
                        "extra_data": sa.extra_data,
                    }
                    for sa in SocialAccount.objects.filter(user=request.user)
                ],
                "ua": ua_string,
                "ip": ip,
                "lastUsed": last_used,
                "deviceInfo": {
                    "deviceName": device_name,
                    "os": os,
                    "browser": browser,
                },
            })

        return Response({"sessions": sessions}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        token_id = request.data.get('token_id')
        if not token_id:
            return Response({"error": "Token ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = OutstandingToken.objects.get(id=token_id, user=request.user)
            # Blacklist the token to invalidate the session
            BlacklistedToken.objects.get_or_create(token=token)
            return Response({"detail": "Session terminated"}, status=status.HTTP_200_OK)
        except OutstandingToken.DoesNotExist:
            return Response({"error": "Invalid or unauthorized token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to terminate session {token_id}: {str(e)}")
            return Response({"error": f"Failed to terminate session: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({"detail": "CSRF cookie set"})