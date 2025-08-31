"""
Legacy social authentication views (deprecated - use social_auth_complete.py)
This file is kept for backward compatibility.
"""

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


# DEPRECATED: Use GoogleSocialLoginView from social_auth_complete.py instead
class GoogleLogin(SocialLoginView):
    """Legacy Google login view - use GoogleSocialLoginView instead"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
    client_class = OAuth2Client
