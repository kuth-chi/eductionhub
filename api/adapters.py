# api/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle social account login flow."""

    def get_login_redirect_url(self, request):
        """
        Redirect to our custom callback view after social login.
        This ensures we process the authentication and redirect to frontend.
        """
        return reverse('social_login_callback')

    def is_auto_signup_allowed(self, request, sociallogin):
        """Allow automatic signup for social accounts."""
        return True

    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Extract additional data from social account
        extra_data = sociallogin.account.extra_data

        if sociallogin.account.provider == 'google':
            if not user.first_name and 'given_name' in extra_data:
                user.first_name = extra_data['given_name']
            if not user.last_name and 'family_name' in extra_data:
                user.last_name = extra_data['family_name']

        elif sociallogin.account.provider == 'facebook':
            if not user.first_name and 'first_name' in extra_data:
                user.first_name = extra_data['first_name']
            if not user.last_name and 'last_name' in extra_data:
                user.last_name = extra_data['last_name']

        elif sociallogin.account.provider == 'telegram':
            if not user.first_name and 'first_name' in extra_data:
                user.first_name = extra_data['first_name']
            if not user.last_name and 'last_name' in extra_data:
                user.last_name = extra_data['last_name']

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save the social account user and create profile if needed.
        """
        user = super().save_user(request, sociallogin, form)

        # Create or update user profile
        from user.models.profile import Profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'email': user.email or '',
            }
        )

        # Update profile with social account data if needed
        if not created:
            updated = False
            if not profile.first_name and user.first_name:
                profile.first_name = user.first_name
                updated = True
            if not profile.last_name and user.last_name:
                profile.last_name = user.last_name
                updated = True
            if not profile.email and user.email:
                profile.email = user.email
                updated = True

            if updated:
                profile.save()

        return user
