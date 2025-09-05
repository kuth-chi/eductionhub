import logging

from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to prevent session hijacking by binding session to user agent and partial IP address.
    In production, uses more flexible validation to account for load balancers and CDNs.
    """

    def _is_production(self):
        """Check if we're in production environment."""
        return getattr(settings, 'SECURE_SSL_REDIRECT', False) or not getattr(settings, 'DEBUG', True)

    def _get_client_ip(self, request):
        """Get client IP with proper proxy header handling."""
        # Check various proxy headers in order of preference
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP (original client) from the chain
            return x_forwarded_for.split(',')[0].strip()

        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()

        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        return request.META.get('REMOTE_ADDR', '')

    def _normalize_ua(self, ua_string):
        """Normalize user agent for more flexible comparison."""
        if not ua_string:
            return ""

        # Remove version numbers and specific build info for more stable matching
        import re

        # Keep browser name and major version, remove minor versions and build numbers
        ua_normalized = re.sub(r'(\d+\.\d+)\.\d+(\.\d+)*', r'\1', ua_string)
        # Remove specific build identifiers
        ua_normalized = re.sub(r'\s+\(.*?\)', '', ua_normalized)
        return ua_normalized.strip()

    def _should_skip_validation(self, request):
        """Determine if we should skip UA/IP validation for this request."""
        # Skip for API endpoints that might be accessed by different clients
        skip_paths = ['/api/', '/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return True

        # Skip if user agent indicates automated/bot access
        ua = request.META.get("HTTP_USER_AGENT", "").lower()
        bot_indicators = ['bot', 'crawler',
                          'spider', 'automated', 'curl', 'wget']
        if any(indicator in ua for indicator in bot_indicators):
            return True

        return False

    def process_request(self, request):
        if not request.user.is_authenticated or self._should_skip_validation(request):
            return None

        session_ua = request.session.get("user_agent")
        session_ip = request.session.get("ip_prefix")
        current_ua = request.META.get("HTTP_USER_AGENT", "")
        current_ip = self._get_client_ip(request)

        # Use only the first two octets of the IP (e.g., '192.168.') for flexibility
        current_ip_prefix = (
            ".".join(current_ip.split(".")[:2]) if current_ip else ""
        )

        if session_ua and session_ip:
            # In production, use more flexible validation
            if self._is_production():
                # Normalize user agents for comparison
                session_ua_normalized = self._normalize_ua(session_ua)
                current_ua_normalized = self._normalize_ua(current_ua)

                # More lenient matching in production
                ua_matches = (
                    session_ua_normalized == current_ua_normalized or
                    # Allow if core browser info is the same
                    any(browser in session_ua_normalized and browser in current_ua_normalized
                        for browser in ['Chrome', 'Firefox', 'Safari', 'Edge']) or
                    # Fallback: if UA is empty, don't fail on UA alone
                    not current_ua.strip()
                )

                # For IP, allow some flexibility in production due to load balancers
                ip_matches = (
                    session_ip == current_ip_prefix or
                    # Allow if in same /16 network (more flexible for cloud environments)
                    (session_ip and current_ip_prefix and
                     session_ip.split('.')[0] == current_ip_prefix.split('.')[0])
                )

                if not ua_matches and not ip_matches:
                    logger.warning(
                        f"Session security violation for user {request.user.id}: "
                        f"UA changed from '{session_ua_normalized}' to '{current_ua_normalized}', "
                        f"IP changed from '{session_ip}' to '{current_ip_prefix}'"
                    )
                    logout(request)
                    request.session.flush()
                elif not ua_matches:
                    logger.info(
                        f"UA changed for user {request.user.id} but IP matches, allowing. "
                        f"UA: '{session_ua_normalized}' -> '{current_ua_normalized}'"
                    )
                    # Update stored UA to current one
                    request.session["user_agent"] = current_ua
                elif not ip_matches:
                    logger.info(
                        f"IP changed for user {request.user.id} but UA matches, allowing. "
                        f"IP: '{session_ip}' -> '{current_ip_prefix}'"
                    )
                    # Update stored IP to current one
                    request.session["ip_prefix"] = current_ip_prefix
            else:
                # Development: strict validation
                if session_ua != current_ua or session_ip != current_ip_prefix:
                    logger.warning(
                        f"Development session security violation for user {request.user.id}"
                    )
                    logout(request)
                    request.session.flush()
        else:
            # First time - store current values
            request.session["user_agent"] = current_ua
            request.session["ip_prefix"] = current_ip_prefix
            logger.info(
                f"Stored session security info for user {request.user.id}")

        return None
