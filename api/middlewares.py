import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class LogRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"Request: {request.method} {request.path}")
        return None


class JWTSessionMiddleware(MiddlewareMixin):
    """
    Middleware to sync JWT tokens with Django sessions for seamless authentication
    """

    def process_request(self, request):
        # Skip for static files and admin
        if request.path.startswith(("/static/", "/media/", "/admin/", "/super-user/")):
            return None

        # Check for JWT token in cookies
        access_token = request.COOKIES.get("access_token")

        if access_token:
            try:
                # Decode and validate JWT token
                token = AccessToken(access_token)
                user_id = token.get("user_id")

                if user_id:
                    # Get user from database
                    from django.contrib.auth import get_user_model

                    User = get_user_model()

                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                        # Set session for Django compatibility
                        request.session["user_id"] = user.pk
                        logger.info(
                            f"JWT authentication successful for user {user.username}"
                        )
                    except User.DoesNotExist:
                        logger.warning(f"User with ID {user_id} not found")
                        request.user = AnonymousUser()

            except TokenError as e:
                logger.warning(f"Invalid JWT token: {e}")
                request.user = AnonymousUser()
                # Clear invalid cookies
                request.COOKIES.pop("access_token", None)
                request.COOKIES.pop("refresh_token", None)

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
