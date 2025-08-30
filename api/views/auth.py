"""Authentication and session management views (DRF + SimpleJWT).

Best practices:
- Token issuance via serializers; set httpOnly cookies (access/refresh) using SIMPLE_JWT lifetimes.
- Refresh from cookie if body missing; respect rotation.
- Explicit permissions; safe logging; narrow exceptions where possible.
- Session listing via OutstandingToken; robust UA parsing; CSRF helper.
"""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Union, cast

import jwt
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from user_agents import parse

from api.serializers.custom_jwt import CustomTokenObtainPairSerializer
from user.models.profile import Profile  # pylint: disable=no-member

logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG
SECURE = not DEBUG


def _get_max_age(value: Union[timedelta, int], fallback_seconds: int) -> int:
    """Safely get max age from timedelta or int value."""
    try:
        if isinstance(value, timedelta):
            return int(value.total_seconds())
        return int(value)
    except (TypeError, ValueError, AttributeError):
        return fallback_seconds


def _validate_jwt_token(token: str) -> bool:
    """Validate JWT token structure and signature."""
    if not token or not isinstance(token, str):
        return False

    # Basic JWT format validation (header.payload.signature)
    jwt_pattern = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'
    if not re.match(jwt_pattern, token):
        return False

    # Additional length check to prevent extremely long tokens
    if len(token) > 4096:  # Reasonable JWT size limit
        return False

    try:
        # Validate token structure without verifying signature
        # (signature validation happens during token use)
        jwt.decode(token, options={"verify_signature": False})
        return True
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return False


def _sanitize_cookie_value(value: str) -> str:
    """Sanitize cookie value to prevent injection attacks."""
    if not value or not isinstance(value, str):
        raise ValidationError("Invalid cookie value")

    # Remove any characters that could be used for cookie injection
    # Keep only JWT-safe characters
    safe_pattern = r'^[A-Za-z0-9._-]+$'
    if not re.match(safe_pattern, value):
        raise ValidationError("Cookie value contains invalid characters")

    return value


def set_auth_cookies(response: Response, access: str, refresh: str) -> Response:
    """
    Set secure authentication cookies with proper validation and security attributes.

    Args:
        response: Django Response object
        access: JWT access token string
        refresh: JWT refresh token string

    Returns:
        Response object with secure cookies set

    Raises:
        ValidationError: If token validation fails
    """
    # Validate and sanitize tokens before setting cookies
    if not _validate_jwt_token(access):
        logger.error("Invalid access token format detected")
        raise ValidationError("Invalid access token format")

    if not _validate_jwt_token(refresh):
        logger.error("Invalid refresh token format detected")
        raise ValidationError("Invalid refresh token format")

    try:
        sanitized_access = _sanitize_cookie_value(access)
        sanitized_refresh = _sanitize_cookie_value(refresh)
    except ValidationError as e:
        logger.error("Token sanitization failed: %s", str(e))
        raise

    # Security-first cookie configuration
    same_site = "Strict"  # Changed from "Lax" to "Strict" for better security
    access_age = _get_max_age(getattr(settings, "SIMPLE_JWT", {}).get(
        "ACCESS_TOKEN_LIFETIME", timedelta(minutes=5)), 300)
    refresh_age = _get_max_age(getattr(settings, "SIMPLE_JWT", {}).get(
        "REFRESH_TOKEN_LIFETIME", timedelta(days=7)), 7 * 24 * 3600)

    # Secure domain configuration
    cookie_domain = None  # Let browser handle domain automatically for security

    # Set access token cookie with secure attributes
    response.set_cookie(
        "access_token",
        sanitized_access,
        httponly=True,  # SECURITY FIX: Prevent JavaScript access to mitigate XSS
        secure=SECURE,  # Only send over HTTPS in production
        samesite=same_site,  # Prevent CSRF attacks
        path="/",
        max_age=access_age,
        domain=cookie_domain,
    )

    # Set refresh token cookie with secure attributes
    response.set_cookie(
        "refresh_token",
        sanitized_refresh,
        httponly=True,  # SECURITY FIX: Prevent JavaScript access to mitigate XSS
        secure=SECURE,  # Only send over HTTPS in production
        samesite=same_site,  # Prevent CSRF attacks
        path="/",
        max_age=refresh_age,
        domain=cookie_domain,
    )

    # Set a separate cookie for frontend to know authentication status
    # This cookie is safe for JavaScript access as it contains no sensitive data
    response.set_cookie(
        "auth_status",
        "authenticated",
        httponly=False,  # Safe for JavaScript access
        secure=SECURE,
        samesite=same_site,
        path="/",
        max_age=access_age,  # Sync with access token expiry
        domain=cookie_domain,
    )

    logger.info("Secure authentication cookies set successfully")
    return response


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        update_last_login(None, user)
        data = serializer.validated_data
        response = Response(data, status=status.HTTP_200_OK)

        try:
            return set_auth_cookies(response, str(data["access"]), str(data["refresh"]))
        except ValidationError as e:
            logger.error("Failed to set authentication cookies: %s", str(e))
            return Response(
                {"error": "Authentication failed due to security validation"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SocialLoginJWTView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

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
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "photo": profile.photo.url if profile.photo else None,
            "is_active": user.is_active,
        }

        for token in [refresh, access]:
            token["profile"] = profile_data
            token["permissions"] = list(user.get_all_permissions())
            token["roles"] = [group.name for group in user.groups.all()]
            token["social_accounts"] = [
                {"provider": sa.provider, "uid": sa.uid, "extra_data": sa.extra_data}
                # type: ignore[attr-defined]  # pylint: disable=no-member
                for sa in SocialAccount.objects.filter(user=user)
            ]
            token["ua"] = request.META.get("HTTP_USER_AGENT", "")
            token["ip"] = get_client_ip(request)

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

        try:
            return set_auth_cookies(response, str(access), str(refresh))
        except ValidationError as e:
            logger.error(
                "Failed to set authentication cookies for social login: %s", str(e))
            return Response(
                {"error": "Authentication failed due to security validation"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out successfully"})
        # type: ignore[attr-defined]  # pylint: disable=no-member
        for token in OutstandingToken.objects.filter(user=request.user):
            # type: ignore[attr-defined]  # pylint: disable=no-member
            BlacklistedToken.objects.get_or_create(token=token)

        # Clear all authentication-related cookies securely
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        # Clear the new auth status cookie
        response.delete_cookie("auth_status", path="/")
        response.delete_cookie("access")  # Legacy cookie cleanup
        response.delete_cookie("refresh")  # Legacy cookie cleanup
        response.delete_cookie("csrftoken")
        if hasattr(request, "session"):
            request.session.flush()
        return response


class AuthStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            # type: ignore[attr-defined]  # pylint: disable=no-member
            social_accounts = SocialAccount.objects.filter(user=request.user)

            ua_string = request.META.get("HTTP_USER_AGENT", "")
            user_agent = parse(ua_string)
            device_info = {
                "device_family": user_agent.device.family,
                "device_brand": user_agent.device.brand,
                "device_model": user_agent.device.model,
                "os_family": user_agent.os.family,
                "os_version": user_agent.os.version_string,
                "browser_family": user_agent.browser.family,
                "browser_version": user_agent.browser.version_string,
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
                "is_pc": user_agent.is_pc,
            }

            return Response(
                {
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
                        {"provider": sa.provider, "uid": sa.uid,
                            "extra_data": sa.extra_data}
                        for sa in social_accounts
                    ],
                    "permissions": list(request.user.get_all_permissions()),
                    "roles": [group.name for group in request.user.groups.all()],
                    "ua": ua_string,
                    "device": device_info,
                    "ip": get_client_ip(request),
                }
            )
        # type: ignore[attr-defined]  # pylint: disable=no-member
        except Profile.DoesNotExist:
            return Response({"authenticated": True, "profile": None}, status=status.HTTP_200_OK)
        # type: ignore[attr-defined]  # pylint: disable=no-member
        except Profile.MultipleObjectsReturned:
            logger.error("Multiple profiles found for user id=%s",
                         request.user.id)
            return Response({"error": "Profile conflict"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:  # pragma: no cover  # pylint: disable=broad-except
            logger.error("Error fetching auth status: %s", str(e))
            return Response({"error": "Failed to fetch auth status"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        logger.info("Token refresh requested from IP: %s",
                    get_client_ip(request))

        body = request.data
        payload = dict(body) if isinstance(body, dict) else {
            **getattr(body, "dict", lambda: {})()}

        # Support both current and legacy cookie names
        cookie_refresh = request.COOKIES.get(
            "refresh_token") or request.COOKIES.get("refresh")

        # Accept both 'refresh' and 'refresh_token' keys in body
        if not payload.get("refresh") and payload.get("refresh_token"):
            payload["refresh"] = payload.get("refresh_token")

        # If no refresh token in body, try to get from cookie
        if not payload.get("refresh") and cookie_refresh:
            payload["refresh"] = cookie_refresh

        # If still no refresh token, return detailed error
        if "refresh" not in payload or not payload["refresh"]:
            available_cookies = list(request.COOKIES.keys())
            logger.warning(
                "Refresh request missing token. Body keys: %s, Cookies present: %s",
                list(payload.keys()),
                available_cookies
            )
            return Response({
                "error": "No refresh token provided",
                "detail": "Refresh token must be provided in request body or cookies",
                "debug": {
                    "body_keys": list(payload.keys()),
                    "cookies_available": available_cookies,
                    "expected_fields": ["refresh", "refresh_token"]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        from rest_framework_simplejwt.exceptions import (InvalidToken,
                                                         TokenError)
        try:
            serializer = self.get_serializer(data=payload)
            serializer.is_valid(raise_exception=True)
        except (TokenError, InvalidToken) as e:
            logger.warning("Invalid refresh token: %s", str(e))
            return Response({
                "error": "Invalid refresh token",
                "detail": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

        response_data = serializer.validated_data
        new_access = cast(dict, response_data).get("access")
        new_refresh = cast(dict, response_data).get(
            "refresh") or payload["refresh"]

        response = Response(response_data, status=status.HTTP_200_OK)
        if new_access:
            try:
                response = set_auth_cookies(
                    response, str(new_access), str(new_refresh))
            except ValidationError as e:
                logger.error(
                    "Failed to set authentication cookies during refresh: %s", str(e))
                return Response(
                    {"error": "Token refresh failed due to security validation"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return response


class ActiveSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        # type: ignore[attr-defined]  # pylint: disable=no-member
        except Profile.DoesNotExist:
            logger.warning("No profile found for user %s", request.user.id)
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        sessions = []
        # type: ignore[attr-defined]  # pylint: disable=no-member
        tokens = OutstandingToken.objects.filter(user=request.user)

        for token in tokens:
            try:
                signing_key = getattr(
                    jwt_api_settings, "SIGNING_KEY", None) or settings.SECRET_KEY
                algorithm = getattr(jwt_api_settings, "ALGORITHM", "HS256")
                token_data = jwt.decode(
                    token.token,
                    signing_key,
                    algorithms=[algorithm],
                    options={"verify_exp": False},
                )
            except jwt.InvalidTokenError as e:
                logger.debug("Skipping invalid token %s: %s",
                             str(token.id), str(e))
                continue

            ua_string = token_data.get("ua", "")
            ip = token_data.get("ip", "")
            last_used = token.created_at.isoformat() if getattr(
                token, "created_at", None) else None

            device_name, os_name, browser = "Unknown Device", "Unknown OS", "Unknown Browser"
            if ua_string:
                try:
                    user_agent = parse(ua_string)
                    brand = getattr(user_agent.device, "brand", "") or ""
                    model = getattr(user_agent.device, "model", "") or ""
                    candidate = f"{brand} {model}".strip()
                    if candidate:
                        device_name = candidate
                    os_family = getattr(user_agent.os, "family", "") or ""
                    os_version = getattr(
                        user_agent.os, "version_string", "") or ""
                    candidate = f"{os_family} {os_version}".strip()
                    if candidate:
                        os_name = candidate
                    browser_family = getattr(
                        user_agent.browser, "family", "") or ""
                    browser_version = getattr(
                        user_agent.browser, "version_string", "") or ""
                    candidate = f"{browser_family} {browser_version}".strip()
                    if candidate:
                        browser = candidate
                except Exception as e:  # UA parsing safety  # pylint: disable=broad-except
                    logger.error(
                        "Failed to parse user agent '%s': %s", ua_string, str(e))

            sessions.append(
                {
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
                        {"provider": sa.provider, "uid": sa.uid,
                            "extra_data": sa.extra_data}
                        # type: ignore[attr-defined]  # pylint: disable=no-member
                        for sa in SocialAccount.objects.filter(user=request.user)
                    ],
                    "ua": ua_string,
                    "ip": ip,
                    "lastUsed": last_used,
                    "deviceInfo": {"deviceName": device_name, "os": os_name, "browser": browser},
                }
            )

        return Response({"sessions": sessions}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        token_id = request.data.get("token_id")
        if not token_id:
            return Response({"error": "Token ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # type: ignore[attr-defined]  # pylint: disable=no-member
            token = OutstandingToken.objects.get(
                id=token_id, user=request.user)
            # type: ignore[attr-defined]  # pylint: disable=no-member
            BlacklistedToken.objects.get_or_create(token=token)
            return Response({"detail": "Session terminated"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Invalid or unauthorized token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # pragma: no cover  # pylint: disable=broad-except
            logger.error("Failed to terminate session %s: %s",
                         str(token_id), str(e))
            return Response({"error": "Failed to terminate session"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ensure_csrf_cookie
def csrf_token_view(_request):
    return JsonResponse({"detail": "CSRF cookie set"})


# Duplicate SocialLoginJWTView class removed to resolve redefinition error.
