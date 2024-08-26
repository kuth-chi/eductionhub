""" User Profile middleware """
from django.utils.deprecation import MiddlewareMixin
# Internal import
from user.models import Profile


class EnsureProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user = request.user
            # Use get_or_create to ensure a profile exists
            Profile.objects.get_or_create(user=user)
