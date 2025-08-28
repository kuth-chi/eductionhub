from datetime import datetime
from typing import Any, Dict, Optional

from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from user.models.profile import Profile


def sanitize_extra_data(data):
    """Recursively convert datetime objects to ISO strings for JWT compatibility."""
    if isinstance(data, dict):
        return {k: sanitize_extra_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_extra_data(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = str(user.pk)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user is None:
            raise serializers.ValidationError("User authentication failed.")

        request = self.context.get("request", None)

        # Issue tokens
        # This returns a RefreshToken
        refresh_token = self.get_token(self.user)
        # Get the access token from refresh token
        access_token = refresh_token.access_token

        # Get or create user profile
        profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                "first_name": self.user.first_name or "",
                "last_name": self.user.last_name or "",
                "email": self.user.email or "",
            },
        )

        profile_data = {
            "id": str(profile.uuid),
            "first_name": profile.user.first_name,
            "last_name": profile.user.last_name,
            "email": profile.user.email,
            "last_login": profile.user.last_login.isoformat() if profile.user.last_login else None,
            "is_active": profile.user.is_active,
            "photo": profile.photo.url if profile.photo else None,
        }

        # Inject custom claims into both tokens - keep minimal for size
        common_claims = {
            "profile": {
                "id": str(profile.uuid),
                "first_name": profile.user.first_name,
                "last_name": profile.user.last_name,
                "email": profile.user.email,
                "is_active": profile.user.is_active,
            },
            # Include essential permissions/roles to keep token size manageable
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
            # Store role names from Django groups and RBAC roles
            "roles": self._get_user_roles(),
            "permissions": self._get_essential_permissions(),
        }

        for token in [access_token, refresh_token]:
            for key, value in common_claims.items():
                token[key] = value

        # Add user-agent and full IP
        if request:
            token_ip = request.META.get("REMOTE_ADDR", "")
            token_ua = request.META.get("HTTP_USER_AGENT", "")
            access_token["ip"] = token_ip
            access_token["ua"] = token_ua
            refresh_token["ip"] = token_ip
            refresh_token["ua"] = token_ua

        # Return string versions of the tokens
        data["access"] = str(access_token)
        data["refresh"] = str(refresh_token)

        return data

    def _get_user_roles(self):
        """Get all roles for the user from groups and RBAC system."""
        roles = []

        # Get roles from Django groups
        roles.extend([g.name for g in self.user.groups.all()])

        # Get roles from RBAC system if available
        try:
            from organization.models.employee import Employee
            from rbac.models.role_assignment import RoleAssignment

            employee = Employee.objects.get(user=self.user)
            rbac_roles = [
                assignment.role.name
                for assignment in RoleAssignment.objects.filter(
                    employee=employee,
                    is_active=True,
                    is_deleted=False
                )
            ]
            roles.extend(rbac_roles)
        except (ImportError, Employee.DoesNotExist):
            pass

        # Remove duplicates and return
        return list(set(roles))

    def _get_essential_permissions(self):
        """Get essential permissions for quick token-based checks."""
        permissions = {
            'can_delete_schools': False,
            'can_manage_colleges': False,
            'can_manage_branches': False,
            'can_view_analytics': False,
        }

        # Superuser has all permissions
        if self.user.is_superuser:
            return {key: True for key in permissions.keys()}

        # Get user roles
        user_roles = self._get_user_roles()

        # Set permissions based on roles
        if 'SuperAdmin' in user_roles:
            permissions.update({
                'can_delete_schools': True,
                'can_manage_colleges': True,
                'can_manage_branches': True,
                'can_view_analytics': True,
            })
        elif 'Administrator' in user_roles:
            permissions.update({
                'can_manage_colleges': True,
                'can_manage_branches': True,
                'can_view_analytics': True,
            })
        elif 'Manager' in user_roles:
            permissions.update({
                'can_manage_colleges': True,
                'can_manage_branches': True,
            })
        elif 'Staff' in user_roles:
            permissions.update({
                'can_manage_colleges': True,
            })

        return permissions
