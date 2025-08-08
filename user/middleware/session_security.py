from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to prevent session hijacking by binding session to user agent and partial IP address.
    If user agent or IP changes, the user is logged out.
    """

    def process_request(self, request):
        if request.user.is_authenticated:
            session_ua = request.session.get("user_agent")
            session_ip = request.session.get("ip_prefix")
            current_ua = request.META.get("HTTP_USER_AGENT", "")
            current_ip = request.META.get("REMOTE_ADDR", "")
            # Use only the first two octets of the IP (e.g., '192.168.') for flexibility
            current_ip_prefix = (
                ".".join(current_ip.split(".")[:2]) if current_ip else ""
            )
            if session_ua and session_ip:
                if session_ua != current_ua or session_ip != current_ip_prefix:
                    logout(request)
                    request.session.flush()
            else:
                request.session["user_agent"] = current_ua
                request.session["ip_prefix"] = current_ip_prefix
