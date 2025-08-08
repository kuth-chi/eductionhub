# rbac/views/organization_permissions.py

from rest_framework.permissions import BasePermission
from organization.models.employee import Employee


class OrganizationPermission(BasePermission):
    """
    Custom DRF permission that checks user role + model permission
    within the organization context (RBAC + ABAC).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # The view must define the organization context (e.g., via get_object or a decorator)
        organization = getattr(view, 'organization', None)
        if not organization:
            return False

        # Resolve model and permission codename
        model_name = view.queryset.model._meta.model_name
        app_label = view.queryset.model._meta.app_label
        action = self.map_method_to_permission(request.method)

        if not action:
            return False

        permission_codename = f"{action}_{model_name}"

        # Get employee for this user/org
        try:
            employee = Employee.objects.get(user=user, organization=organization)
        except Employee.DoesNotExist:
            return False

        # --- RBAC Check ---
        if not employee.role_assignments.filter(role__permissions__codename=permission_codename).exists():
            return False

        # --- ABAC Check (optional) ---
        if hasattr(view, 'abac_context'):
            abac_context = view.abac_context  # should be a dict like {"department": "IT"}
            if not self.check_abac(employee, permission_codename, abac_context):
                return False

        return True

    def map_method_to_permission(self, method: str) -> str | None:
        """
        Maps HTTP methods to Django's default permissions.
        """
        return {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }.get(method.upper())

    def check_abac(self, employee: Employee, permission_codename: str, abac_context: dict) -> bool:
        """
        Validate ABAC policy: only return True if there's a matching
        key=value pair in the context that aligns with role assignment.
        """
        for assignment in employee.role_assignments.filter(role__permissions__codename=permission_codename, is_active=True, is_deleted=False):
            if assignment.key in abac_context and abac_context[assignment.key] == assignment.value:
                return True
        return False
