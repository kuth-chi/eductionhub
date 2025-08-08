# schools/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSchoolCreatorOrAdmin(BasePermission):
    """
    Allows school creators or admins to modify objects.
    Assumes obj.created_by exists.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            obj.created_by == request.user or
            request.user.is_staff
        )

