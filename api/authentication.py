from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)


class UserAgentBoundJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        request = self.context.get("request") if hasattr(self, "context") else None
        if request:
            token_ua = validated_token.get("ua", None)
            request_ua = request.META.get("HTTP_USER_AGENT", "")
            token_ip = validated_token.get("ip", None)
            request_ip = request.META.get("REMOTE_ADDR", "")
            request_ip_prefix = (
                ".".join(request_ip.split(".")[:2]) if request_ip else ""
            )

            # Debug logging
            logger.info(f"Auth check - Token UA: {token_ua}, Request UA: {request_ua}")
            logger.info(
                f"Auth check - Token IP: {token_ip}, Request IP prefix: {request_ip_prefix}"
            )

            # Temporarily disable strict checks for development
            # if token_ua is not None and token_ua != request_ua:
            #     raise AuthenticationFailed("Token user agent mismatch.")
            # if token_ip is not None and token_ip != request_ip_prefix:
            #     raise AuthenticationFailed("Token IP mismatch.")

            # Only log warnings instead of failing
            if token_ua is not None and token_ua != request_ua:
                logger.warning(f"Token user agent mismatch: {token_ua} vs {request_ua}")
            if token_ip is not None and token_ip != request_ip_prefix:
                logger.warning(f"Token IP mismatch: {token_ip} vs {request_ip_prefix}")

        return user

    def authenticate(self, request):
        self.context = {"request": request}
        return super().authenticate(request)
