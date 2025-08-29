# rbac/permissions.py
"""
Role-Based Access Control (RBAC) Permissions

This module provides custom permission classes for Django REST Framework
that implement role-based and organization-based access control.
"""

import logging


from rest_framework import permissions
from rest_framework.permissions import BasePermission

from organization.models.employee import Employee
from rbac.models.role_assignment import RoleAssignment

logger = logging.getLogger(__name__)


class RoleBasedPermission(BasePermission):
    """
    Base permission class that implements role-based access control.

    This permission class checks if the authenticated user has the required
    roles to perform specific actions on resources.
    """

    # Define required roles for different actions
    required_roles = {
        'list': [],  # Anyone can list (handled by other permissions)
        'retrieve': [],  # Anyone can retrieve (handled by other permissions)
        'create': ['Administrator', 'Manager', 'Staff'],
        'update': ['Administrator', 'Manager', 'Staff'],
        'partial_update': ['Administrator', 'Manager', 'Staff'],
        'destroy': ['Administrator', 'SuperAdmin'],  # Only admins can delete
    }

    def has_permission(self, request, view):
        """
        Check if user has permission to perform the action.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Get the action being performed
        action = getattr(view, 'action', None)
        if not action:
            return True

        # Check if specific roles are required for this action
        required_roles = self.required_roles.get(action, [])
        if not required_roles:
            return True

        # Get user's roles from JWT token or database
        user_roles = self._get_user_roles(request.user, request)

        # Check if user has any of the required roles
        has_required_role = any(role in user_roles for role in required_roles)

        if not has_required_role:
            logger.warning(
                "Access denied: User %s attempted %s but lacks required roles %s. User roles: %s",
                request.user.username, action, required_roles, user_roles
            )

        return has_required_role

    def _get_user_roles(self, user, request):
        """
        Get user roles from JWT token or database.
        """
        # First try to get roles from JWT token
        if hasattr(request, 'auth') and request.auth:
            try:
                # Access the token payload
                token_roles = getattr(
                    request.auth, 'payload', {}).get('roles', [])
                if token_roles:
                    return token_roles
            except (AttributeError, KeyError):
                pass

        # Fallback to database lookup
        try:
            # Get roles from Django groups (basic implementation)
            group_roles = [group.name for group in user.groups.all()]

            # Get roles from RBAC system if user is an employee
            try:
                employee = Employee.objects.get(user=user)
                rbac_roles = [
                    assignment.role.name
                    for assignment in RoleAssignment.objects.filter(
                        employee=employee,
                        is_active=True,
                        is_deleted=False
                    )
                ]
                return list(set(group_roles + rbac_roles))
            except Employee.objects.model.DoesNotExist:
                return group_roles

        except Employee.objects.model.DoesNotExist:
            return []
        except (AttributeError, KeyError) as e:
            logger.error("Error getting user roles: %s", e)
            return []


class SchoolPermission(RoleBasedPermission):
    """
    Permission class specifically for School resources.

    Schools are critical infrastructure, so we require higher permissions
    for modifications and deletions.
    """

    required_roles = {
        'list': [],  # Public access
        'retrieve': [],  # Public access
        'create': ['Administrator', 'SuperAdmin'],  # Only high-level admins
        'update': ['Administrator', 'SuperAdmin'],
        'partial_update': ['Administrator', 'SuperAdmin'],
        'destroy': ['SuperAdmin'],  # Only super admins can delete schools
    }


class CollegePermission(RoleBasedPermission):
    """
    Permission class for College resources.

    Colleges can be managed by school administrators and staff.
    """

    required_roles = {
        'list': [],  # Public access
        'retrieve': [],  # Public access
        'create': ['Administrator', 'Manager', 'Staff'],
        'update': ['Administrator', 'Manager', 'Staff'],
        'partial_update': ['Administrator', 'Manager', 'Staff'],
        # Managers and above can delete
        'destroy': ['Administrator', 'Manager'],
    }


class BranchPermission(RoleBasedPermission):
    """
    Permission class for Branch resources.
    """

    required_roles = {
        'list': [],  # Public access
        'retrieve': [],  # Public access
        'create': ['Administrator', 'Manager', 'Staff'],
        'update': ['Administrator', 'Manager', 'Staff'],
        'partial_update': ['Administrator', 'Manager', 'Staff'],
        'destroy': ['Administrator', 'Manager'],
    }


class OrganizationScopedPermission(BasePermission):
    """
    Permission that restricts access based on organization membership.

    Users can only access resources that belong to their organization.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access this specific object.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have access to everything
        if request.user.is_superuser:
            return True

        # Check if user belongs to the same organization as the object
        user_organizations = self._get_user_organizations(request.user)
        obj_organization = self._get_object_organization(obj)

        if obj_organization and obj_organization in user_organizations:
            return True

        logger.warning(
            "Organization access denied: User %s attempted to access %r from organization %r, but user belongs to %r",
            request.user.username, obj, obj_organization, user_organizations
        )

        return False

    def _get_user_organizations(self, user):
        """Get organizations that the user belongs to."""
        try:
            employee = Employee.objects.get(user=user)
            return [employee.organization]
        except Employee.objects.model.DoesNotExist:
            return []

    def _get_object_organization(self, obj):
        """Get the organization that owns this object."""
        # This method should be overridden by subclasses
        # to handle different object types

        # Common patterns:
        if hasattr(obj, 'organization'):
            return obj.organization
        elif hasattr(obj, 'school') and hasattr(obj.school, 'organization'):
            return obj.school.organization
        elif hasattr(obj, 'branch') and hasattr(obj.branch, 'school') and hasattr(obj.branch.school, 'organization'):
            return obj.branch.school.organization

        return None


# Composite permissions combining role and organization checks
class SchoolManagementPermission(permissions.BasePermission):
    """
    Composite permission for comprehensive school management access control.
    """

    def has_permission(self, request, view):
        # First check role-based permissions
        role_permission = SchoolPermission()
        if not role_permission.has_permission(request, view):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Then check organization-scoped permissions for specific objects
        org_permission = OrganizationScopedPermission()
        return org_permission.has_object_permission(request, view, obj)


class CollegeManagementPermission(permissions.BasePermission):
    """
    Composite permission for comprehensive college management access control.
    """

    def has_permission(self, request, view):
        role_permission = CollegePermission()
        return role_permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        org_permission = OrganizationScopedPermission()
        return org_permission.has_object_permission(request, view, obj)


# Utility functions for permission checking
def user_has_role(user, role_name):
    """
    Check if a user has a specific role.
    """
    try:
        employee = Employee.objects.get(user=user)
        return RoleAssignment.objects.filter(
            employee=employee,
            role__name=role_name,
            is_active=True,
            is_deleted=False
        ).exists()
    except Employee.objects.model.DoesNotExist:
        return user.groups.filter(name=role_name).exists()


def user_can_delete_schools(user):
    """
    Check if user has permission to delete schools.
    """
    return user.is_superuser or user_has_role(user, 'SuperAdmin')


def user_can_manage_colleges(user):
    """
    Check if user has permission to manage colleges.
    """
    return (user.is_superuser or
            user_has_role(user, 'Administrator') or
            user_has_role(user, 'Manager') or
            user_has_role(user, 'Staff'))
