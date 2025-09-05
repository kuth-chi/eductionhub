import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


class LogRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"Request: {request.method} {request.path}")
        return None


class JWTSessionMiddleware(MiddlewareMixin):
    """
    Middleware to sync JWT tokens with Django sessions for seamless authentication.
    Uses production-safe validation that accounts for proxy environments.
    """

    def _is_production(self):
        """Check if we're in production environment."""
        return getattr(settings, 'SECURE_SSL_REDIRECT', False) or not getattr(settings, 'DEBUG', True)

    def _get_client_ip(self, request):
        """Get client IP with proper proxy header handling."""
        # Check various proxy headers in order of preference
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()

        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()

        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        return request.META.get('REMOTE_ADDR', '')

    def _validate_token_context(self, token_payload, request):
        """Validate token context (IP/UA) with production-safe rules."""
        if not self._is_production():
            # Development: no additional validation
            return True

        # Production: flexible validation
        token_ip = token_payload.get('ip', '')
        token_ua = token_payload.get('ua', '')
        current_ip = self._get_client_ip(request)
        current_ua = request.META.get('HTTP_USER_AGENT', '')

        # IP validation: allow same /24 network (first 3 octets)
        if token_ip and current_ip:
            token_ip_parts = token_ip.split('.')[:3]
            current_ip_parts = current_ip.split('.')[:3]
            ip_matches = token_ip_parts == current_ip_parts
        else:
            ip_matches = True  # Allow if either is missing

        # UA validation: check for core browser compatibility
        if token_ua and current_ua:
            # Extract browser family for comparison
            import re

            def extract_browser_family(ua):
                browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
                for browser in browsers:
                    if browser in ua:
                        return browser
                return 'Unknown'

            token_browser = extract_browser_family(token_ua)
            current_browser = extract_browser_family(current_ua)
            ua_matches = token_browser == current_browser
        else:
            ua_matches = True  # Allow if either is missing

        # Log validation results for debugging
        if not (ip_matches and ua_matches):
            logger.warning(
                f"Token context validation failed: "
                f"IP match: {ip_matches} ({token_ip} vs {current_ip}), "
                f"UA match: {ua_matches} ({token_ua[:50] if token_ua else 'None'} vs {current_ua[:50] if current_ua else 'None'})"
            )

        # In production, be more lenient - allow if either IP or UA matches
        return ip_matches or ua_matches

    def process_request(self, request):
        # Skip for static files and admin
        if request.path.startswith(("/static/", "/media/", "/admin/", "/super-user/")):
            return None

        # Check for JWT token in cookies (try multiple cookie names)
        access_token = (
            request.COOKIES.get("access_token") or
            request.COOKIES.get("__Host-access_token") or
            request.COOKIES.get("__Secure-access_token")
        )

        if access_token:
            try:
                # Decode and validate JWT token
                token = AccessToken(access_token)
                user_id = token.get("user_id")

                if user_id:
                    # Validate token context (IP/UA) if in production
                    if not self._validate_token_context(token.payload, request):
                        logger.warning(
                            f"Token context validation failed for user {user_id}")
                        request.user = AnonymousUser()
                        return None

                    # Get user from database
                    from django.contrib.auth import get_user_model

                    User = get_user_model()

                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                        # Set session for Django compatibility
                        request.session["user_id"] = user.pk
                        logger.debug(
                            f"JWT authentication successful for user {user.username}"
                        )
                    except User.DoesNotExist:
                        logger.warning(f"User with ID {user_id} not found")
                        request.user = AnonymousUser()

            except TokenError as e:
                logger.warning(f"Invalid JWT token: {e}")
                request.user = AnonymousUser()
                # Clear invalid cookies - but don't modify the request.COOKIES dict directly
                # Let the client handle cookie clearing through response headers

        return None


class SocialAuthMiddleware(MiddlewareMixin):
    """
    Middleware to handle social authentication redirects and token generation
    """

    def process_response(self, request, response):
        # Check if this is a social login redirect
        if (
            request.path.startswith("/accounts/")
            and request.user.is_authenticated
            and "socialaccount" in request.path
        ):

            # Set a flag to indicate social login completion
            response.set_cookie(
                "social_login_complete",
                "true",
                max_age=300,  # 5 minutes
                httponly=False,
                secure=False,
                samesite="Lax",
            )

        return response


class RequestContextLoggingMiddleware(MiddlewareMixin):
    """
    Adds a unique request ID and logs request/response summary with safe
    authentication signals (without exposing token values).
    Also returns X-Request-ID header for correlation across services.
    """

    def process_request(self, request):
        request.request_id = str(uuid.uuid4())  # type: ignore[attr-defined]
        # Basic request start log with client IP and origin
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(
            ",")[0].strip() or request.META.get("REMOTE_ADDR", "")
        origin = request.META.get("HTTP_ORIGIN", "")
        host = request.get_host()
        logger.info(
            "req start | id=%s method=%s path=%s ip=%s host=%s origin=%s",
            getattr(request, "request_id",
                    "-"), request.method, request.path, ip, host, origin,
        )
        return None

    def process_response(self, request, response):
        try:
            rid = getattr(request, "request_id", "-")
            # Safe auth cookie presence (do not log values)
            cookies = request.COOKIES or {}
            has_at = "access_token" in cookies or "__Host-access_token" in cookies
            has_rt = "refresh_token" in cookies or "__Host-refresh_token" in cookies
            authz = bool(request.META.get("HTTP_AUTHORIZATION"))
            user = getattr(request, "user", None)
            uid = getattr(user, "id", None)
            uname = getattr(user, "username", None)
            is_auth = bool(getattr(user, "is_authenticated", False))
            logger.info(
                "req end   | id=%s status=%s method=%s path=%s user_id=%s user=%s is_auth=%s has_access_cookie=%s has_refresh_cookie=%s has_authz_header=%s",
                rid, getattr(response, "status_code", "-"), getattr(request, "method", "-"), getattr(
                    request, "path", "-"), uid, uname, is_auth, has_at, has_rt, authz,
            )
            # Echo request id in response header for cross-system tracing
            response["X-Request-ID"] = rid
        except Exception:  # pragma: no cover
            # Never let logging break the response
            pass
        return response
