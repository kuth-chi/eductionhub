# organization/models/employee.py

import uuid
from django.db import models
from django.conf import settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rbac.models.role_assignment import RoleAssignment

class Employee(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    organization = models.ForeignKey(
        'organization.Organization',
        on_delete=models.CASCADE,
        related_name='employees'
    )
    position = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    # CHECK: If you want to use RoleAssignment in Employee, ensure it's imported correctly
    role_assignments: 'models.Manager[RoleAssignment]'

    class Meta:
        unique_together = ('user', 'organization')
        indexes = [
            models.Index(fields=['user', 'organization']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]

    def __str__(self):
        return f"{self.user} @ {self.organization}"

    # === RBAC ===
    def get_roles(self):
        return self.role_assignments.filter(is_active=True, is_deleted=False).values_list('role', flat=True)

    def get_permissions(self):
        """
        Return all permission codenames linked through roles.
        """
        return set(
            self.role_assignments
            .filter(is_active=True, is_deleted=False)
            .values_list('role__permissions__codename', flat=True)
        )

    def has_permission(self, codename: str) -> bool:
        return codename in self.get_permissions()

    # === ABAC ===
    def has_abac_permission(self, codename: str, context: dict) -> bool:
        """
        Check if employee has permission under the ABAC context.
        context should be a dict like {"department": "IT"}
        """
        return self.role_assignments.filter(
            role__permissions__codename=codename,
            key__in=context.keys(),
            value__in=context.values(),
            is_active=True,
            is_deleted=False
        ).exists()
