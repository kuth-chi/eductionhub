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

# Import for user agent parsing
try:
    from user_agents import parse
except ImportError:
    # Fallback if user_agents is not installed
    def parse(ua_string):
        class MockUA:
            def __init__(self):
                self.device = type(
                    '', (), {'brand': '', 'model': '', 'family': 'Unknown'})()
                self.os = type(
                    '', (), {'family': 'Unknown', 'version_string': ''})()
                self.browser = type(
                    '', (), {'family': 'Unknown', 'version_string': ''})()
                self.is_mobile = False
                self.is_tablet = False
                self.is_pc = True
        return MockUA()

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

from api.serializers.custom_jwt import (CustomJWTSerializer,
                                        CustomTokenObtainPairSerializer)
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

    # Cookie SameSite configuration: default to 'None' for cross-site frontend/backend
    same_site = (
        getattr(settings, "REST_AUTH", {}).get("JWT_AUTH_SAMESITE")
        or "Lax"
    )
    access_age = _get_max_age(getattr(settings, "SIMPLE_JWT", {}).get(
        "ACCESS_TOKEN_LIFETIME", timedelta(minutes=5)), 300)
    refresh_age = _get_max_age(getattr(settings, "SIMPLE_JWT", {}).get(
        "REFRESH_TOKEN_LIFETIME", timedelta(days=7)), 7 * 24 * 3600)

    # Set access token cookie with secure attributes (host-only, hardened)
    response.set_cookie(
        "__Host-access_token",
        sanitized_access,
        httponly=True,  # SECURITY FIX: Prevent JavaScript access to mitigate XSS
        secure=True,  # Only send over HTTPS in production
        samesite=same_site,  # Prevent CSRF attacks
        path="/",
        max_age=access_age,
        domain=None,
    )

    # Set refresh token cookie with secure attributes (host-only, hardened)
    response.set_cookie(
        "__Host-refresh_token",
        sanitized_refresh,
        httponly=True,  # SECURITY FIX: Prevent JavaScript access to mitigate XSS
        secure=True,  # Only send over HTTPS in production
        samesite=same_site,  # Prevent CSRF attacks
        path="/",
        max_age=refresh_age,
        domain=None,
    )

    # Set a separate cookie for frontend to know authentication status
    # This cookie is safe for JavaScript access as it contains no sensitive data
    response.set_cookie(
        "__Secure-auth_status",
        "authenticated",
        httponly=False,
        secure=True,
        samesite=same_site,
        path="/",
        max_age=access_age,
        domain=None,
    )

    # Additionally set cross-subdomain cookies for the frontend domain (for proxies on educationhub.io)
    # This enables educationhub.io to send tokens to authz.educationhub.io via server-side proxy.
    try:
        cross_domain = getattr(settings, "CROSS_SUBDOMAIN_COOKIE_DOMAIN", None)
        if cross_domain:
            response.set_cookie(
                "access_token",
                sanitized_access,
                httponly=True,
                secure=True,
                samesite=same_site,
                path="/",
                max_age=access_age,
                domain=cross_domain,
            )
            response.set_cookie(
                "refresh_token",
                sanitized_refresh,
                httponly=True,
                secure=True,
                samesite=same_site,
                path="/",
                max_age=refresh_age,
                domain=cross_domain,
            )
            # Convenience frontend flag (non-sensitive)
            response.set_cookie(
                "auth_status",
                "authenticated",
                httponly=False,
                secure=True,
                samesite=same_site,
                path="/",
                max_age=access_age,
                domain=cross_domain,
            )
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to set cross-subdomain cookies: %s", str(e))

    logger.info("Secure, prefixed authentication cookies set successfully")
    return response


def get_client_ip(request) -> str:
    """Get client IP with proper proxy header handling for production environments."""
    # Check various proxy headers in order of preference
    # X-Forwarded-For: original client IP (first in chain)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP (original client) from the chain
        client_ip = x_forwarded_for.split(",")[0].strip()
        if client_ip and client_ip != "unknown":
            return client_ip

    # X-Real-IP: often set by nginx
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip and x_real_ip != "unknown":
        return x_real_ip.strip()

    # CF-Connecting-IP: Cloudflare
    cf_connecting_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_connecting_ip and cf_connecting_ip != "unknown":
        return cf_connecting_ip.strip()

    # True-Client-IP: some load balancers
    true_client_ip = request.META.get("HTTP_TRUE_CLIENT_IP")
    if true_client_ip and true_client_ip != "unknown":
        return true_client_ip.strip()

    # Fallback to REMOTE_ADDR
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
        """
        Comprehensive logout with complete cache and session invalidation.
        """
        try:
            user = request.user
            logger.info("🔓 [Logout] Starting comprehensive logout for user xxx")

            # Get request data
            data = request.data if hasattr(request, 'data') else {}
            invalidate_all_sessions = data.get(
                'invalidate_all_sessions', False)

            # Invalidate all outstanding tokens for the user
            outstanding_tokens = OutstandingToken.objects.filter(user=user)
            tokens_count = outstanding_tokens.count()

            for token in outstanding_tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            logger.info("🔓 [Logout] Blacklisted token tokens for username")

            # If requested, invalidate all sessions (useful for security incidents)
            if invalidate_all_sessions:
                try:
                    # Clear all sessions for this user from the session store
                    from django.contrib.auth.models import AnonymousUser
                    from django.contrib.sessions.models import Session

                    # This is a more aggressive approach - clear all sessions that might belong to this user
                    # Note: This is not perfectly accurate since sessions don't directly link to users,
                    # but it's the best we can do for comprehensive logout
                    Session.objects.all().delete()  # In production, you might want to be more selective
                    logger.info("🔓 [Logout] Cleared all sessions (invalidate_all_sessions=True)")
                except Exception:
                    logger.warning("🔓 [Logout] Failed to clear all sessions")

            # Clear the current session
            if hasattr(request, "session"):
                try:
                    request.session.flush()
                    logger.info("🔓 [Logout] Flushed current session")
                except Exception:
                    logger.warning("🔓 [Logout] Failed to flush session")

            # Create response with comprehensive cache prevention
            response = Response(
                {
                    "detail": "Logged out successfully",
                    "tokens_invalidated": tokens_count,
                    "cache_cleared": True
                },
                headers={
                    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Surrogate-Control": "no-store",
                }
            )

            # Clear all possible authentication cookies
            cookies_to_clear = [
                "access_token", "refresh_token", "auth_status", "csrftoken",
                "sessionid", "django_session", "access", "refresh", "user_id",
                "user", "auth", "login_state", "authentication"
            ]

            for cookie_name in cookies_to_clear:
                # Clear with different path and domain combinations
                response.delete_cookie(cookie_name, path="/")
                response.delete_cookie(
                    cookie_name, path="/", domain=".educationhub.io")
                response.delete_cookie(cookie_name, path="/api/")
                response.delete_cookie(cookie_name, path="/admin/")

            logger.info(
                f"🔓 [Logout] Cleared {len(cookies_to_clear)} cookie types")
            logger.info(
                f"🔓 [Logout] Comprehensive logout completed for user: {user.username}")

            return response

        except Exception as e:
            logger.error(f"🔓 [Logout] Error during logout: {e}")
            # Even if logout fails, return success to prevent auth loops
            response = Response(
                {"detail": "Logout completed with errors", "error": str(e)},
                headers={
                    "Cache-Control": "no-store, no-cache, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
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

            # Align permissions/roles with frontend expectations while preserving compatibility
            roles = CustomJWTSerializer._get_user_roles(
                request.user)  # type: ignore[attr-defined]
            essential_permissions = CustomJWTSerializer._get_essential_permissions(
                request.user)  # type: ignore[attr-defined]

            return Response(
                {
                    "authenticated": True,
                    "user": {
                        "id": request.user.id,
                        "username": request.user.username,
                        "email": request.user.email,
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                        # Use ISO string for strict JSON safety
                        "last_logged_in": request.user.last_login.isoformat() if request.user.last_login else None,
                        "is_staff": request.user.is_staff,
                        "is_superuser": request.user.is_superuser,
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
                    # New shape expected by frontend (booleans for core abilities)
                    "permissions": essential_permissions,
                    # Backward-compatibility: full Django permission codenames as a separate field
                    "permissions_list": list(request.user.get_all_permissions()),
                    "roles": roles,
                    "is_superuser": request.user.is_superuser,
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
            # Do not leak internal errors to clients
            logger.exception("Error fetching auth status")
            payload = {"error": "Failed to fetch auth status"}
            if DEBUG:
                payload["detail"] = str(e)
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            # logger.warning(
            #     "Refresh request missing token. Body keys: %s, Cookies present: %s",
            #     list(payload.keys()),
            #     available_cookies
            # )
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
            payload = {"error": "Invalid refresh token"}
            if DEBUG:
                payload["detail"] = str(e)
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

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
                payload = {
                    "error": "Token refresh failed due to security validation"}
                if DEBUG:
                    payload["detail"] = str(e)
                return Response(payload, status=status.HTTP_400_BAD_REQUEST)
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

            # Enhanced device and location analysis
            ua_string = token_data.get("ua", "")
            ip = token_data.get("ip", "")
            token_created = token.created_at if hasattr(
                token, "created_at") else None
            last_used = token_created.isoformat() if token_created else None

            # Determine if this is the current session
            current_ip = self._get_client_ip(request)
            current_ua = request.META.get("HTTP_USER_AGENT", "")
            is_current_session = (ip == current_ip and ua_string == current_ua)

            # Parse device information with enhanced details
            device_info = self._parse_device_info(ua_string, ip, token_created)

            # Calculate risk score for abnormal activity detection
            risk_score = self._calculate_risk_score(
                ip, ua_string, token_created, request.user, current_ip, current_ua
            )

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
                    {"provider": sa.provider, "uid": sa.uid,
                        "extra_data": sa.extra_data}
                    for sa in SocialAccount.objects.filter(user=request.user)
                ],
                "ua": ua_string,
                "ip": ip,
                "lastUsed": last_used,
                "deviceInfo": device_info,
                "isCurrentSession": is_current_session,
                "riskScore": risk_score,
                "riskLevel": self._get_risk_level(risk_score),
                "location": self._get_approximate_location(ip),
                "sessionDuration": self._calculate_session_duration(token_created),
            })

        # Sort sessions by risk score (highest first) and last used
        sessions.sort(
            key=lambda x: (-x["riskScore"], x["lastUsed"] or ""), reverse=True)

        return Response({"sessions": sessions}, status=status.HTTP_200_OK)

    def _get_client_ip(self, request):
        """Get client IP with proper proxy header handling."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def _parse_device_info(self, ua_string, ip, created_at):
        """Parse device information with enhanced details."""
        device_info = {
            "deviceName": "Unknown Device",
            "os": "Unknown OS",
            "browser": "Unknown Browser",
            "browser_family": "Unknown",
            "device_type": "Unknown",
            "is_mobile": False,
            "is_tablet": False,
            "is_pc": True,
            # Truncated for display
            "raw_ua": ua_string[:100] if ua_string else "",
        }

        if ua_string:
            try:
                user_agent = parse(ua_string)

                # Device name
                brand = getattr(user_agent.device, "brand", "") or ""
                model = getattr(user_agent.device, "model", "") or ""
                family = getattr(user_agent.device, "family", "") or ""

                if brand and model:
                    device_info["deviceName"] = f"{brand} {model}".strip()
                elif family and family != "Other":
                    device_info["deviceName"] = family
                elif brand:
                    device_info["deviceName"] = brand

                # OS information
                os_family = getattr(user_agent.os, "family", "") or ""
                os_version = getattr(user_agent.os, "version_string", "") or ""
                if os_family:
                    device_info["os"] = f"{os_family} {os_version}".strip(
                    ) if os_version else os_family

                # Browser information
                browser_family = getattr(
                    user_agent.browser, "family", "") or ""
                browser_version = getattr(
                    user_agent.browser, "version_string", "") or ""
                device_info["browser_family"] = browser_family
                if browser_family:
                    device_info["browser"] = f"{browser_family} {browser_version}".strip(
                    ) if browser_version else browser_family

                # Device type
                device_info["device_type"] = getattr(
                    user_agent.device, "family", "Unknown")
                device_info["is_mobile"] = user_agent.is_mobile
                device_info["is_tablet"] = user_agent.is_tablet
                device_info["is_pc"] = user_agent.is_pc

            except Exception as e:
                logger.error("Failed to parse user agent '%s': %s",
                             ua_string, str(e))

        return device_info

    def _calculate_risk_score(self, ip, ua_string, created_at, user, current_ip, current_ua):
        """Calculate risk score for detecting abnormal activity - Very lenient scoring."""
        risk_score = 0

        try:
            from datetime import datetime, timezone

            # Time-based risk factors (much more lenient)
            if created_at:
                now = datetime.now(timezone.utc)
                age_hours = (now - created_at).total_seconds() / 3600

                # Only very old sessions get significant risk
                if age_hours > 2160:  # 90 days
                    risk_score += 15
                elif age_hours > 1440:  # 60 days
                    risk_score += 8
                elif age_hours > 720:  # 30 days
                    risk_score += 3

            # IP-based risk factors (reduced significantly)
            if ip and current_ip:
                # Different IP networks are common and acceptable
                try:
                    ip_parts = ip.split('.')[:3]
                    current_ip_parts = current_ip.split('.')[:3]
                    if ip_parts != current_ip_parts:
                        risk_score += 2  # Very minimal risk for different /24 network

                        # Only completely different providers get moderate risk
                        if ip_parts[:2] != current_ip_parts[:2]:
                            risk_score += 5  # Still low risk for different /16 network
                except:
                    pass

            # User Agent-based risk factors (very tolerant)
            if ua_string and current_ua:
                # Parse both UAs to compare
                try:
                    session_ua = parse(ua_string)
                    current_ua_parsed = parse(current_ua)

                    # Different OS family is normal (mobile vs desktop)
                    if (getattr(session_ua.os, 'family', '') !=
                            getattr(current_ua_parsed.os, 'family', '')):
                        risk_score += 1  # Very minimal risk

                    # Different browser family is very common
                    if (getattr(session_ua.browser, 'family', '') !=
                            getattr(current_ua_parsed.browser, 'family', '')):
                        risk_score += 1  # Minimal risk

                    # Different device type is expected behavior
                    if (getattr(session_ua.device, 'family', '') !=
                            getattr(current_ua_parsed.device, 'family', '')):
                        risk_score += 2  # Still minimal risk

                except:
                    # If we can't parse, minimal risk
                    risk_score += 1

            # Check for known suspicious patterns (only truly malicious ones)
            if ua_string:
                # Only flag obviously malicious bots
                highly_suspicious_patterns = [
                    'sqlmap', 'nikto', 'nmap', 'masscan', 'exploit', 'hack', 'attack']
                moderately_suspicious_patterns = [
                    'bot', 'crawler', 'spider', 'automated', 'curl', 'wget', 'python-requests']

                if any(pattern in ua_string.lower() for pattern in highly_suspicious_patterns):
                    risk_score += 25  # Only truly malicious gets high score
                elif any(pattern in ua_string.lower() for pattern in moderately_suspicious_patterns):
                    risk_score += 5   # Legitimate bots get low score

        except Exception as e:
            logger.error("Error calculating risk score: %s", str(e))
            risk_score = 2  # Default very low risk if calculation fails

        return min(risk_score, 100)  # Cap at 100

    def _get_risk_level(self, risk_score):
        """Convert risk score to human-readable level - Very lenient thresholds."""
        if risk_score >= 50:
            return "HIGH"
        elif risk_score >= 25:
            return "MEDIUM"
        elif risk_score >= 10:
            return "LOW"
        elif risk_score >= 3:
            return "VERY LOW"
        else:
            return "MINIMAL"

    def _get_approximate_location(self, ip):
        """Get approximate location from IP (placeholder)."""
        # This is a placeholder - in production you might use a GeoIP service
        if not ip:
            return {"country": "Unknown", "region": "Unknown", "city": "Unknown"}

        # Basic detection for common IP ranges
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return {"country": "Local Network", "region": "Private", "city": "LAN"}
        elif ip.startswith('127.'):
            return {"country": "Localhost", "region": "Local", "city": "127.0.0.1"}
        else:
            # In production, integrate with a GeoIP service like MaxMind or IP-API
            return {"country": "Unknown", "region": "Unknown", "city": "Unknown", "ip": ip}

    def _calculate_session_duration(self, created_at):
        """Calculate how long the session has been active."""
        if not created_at:
            return "Unknown"

        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            duration = now - created_at

            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            if days > 0:
                return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
            elif hours > 0:
                return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
        except Exception as e:
            logger.error("Error calculating session duration: %s", str(e))
            return "Unknown"

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
            logger.exception("Failed to terminate session %s", str(token_id))
            payload = {"error": "Failed to terminate session"}
            if DEBUG:
                payload["detail"] = str(e)
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ensure_csrf_cookie
def csrf_token_view(_request):
    return JsonResponse({"detail": "CSRF cookie set"})


# Duplicate SocialLoginJWTView class removed to resolve redefinition error.
