from rest_framework.permissions import BasePermission

from organization.models.employee import Employee

class OrganizationPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        org = getattr(view, 'organization', None)
        action = request.method.lower()  # map to add/view/change/delete
        model = view.queryset.model._meta.model_name

        if not user or not org:
            return False
        
        employer = Employee.objects.filter(user=user, organization=org).first()
        if not employer:
            return False

        if not employer.has_permission(f"{action}_{model}"):
            return False

        # Optional: ABAC layer
        if hasattr(view, 'abac_context'):
            return employer.has_abac_permission(f"{action}_{model}", view.abac_context)
        
        return True
