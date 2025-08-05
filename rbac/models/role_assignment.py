# rbac/models/role_assignment.py
import uuid
from django.db import models

from organization.models.employee import Employee
from rbac.models.role import Role

class RoleAssignment(models.Model):
    # ABAC attributes
    key = models.CharField(max_length=255, blank=True) # e.g., department, location, etc.
    value = models.CharField(max_length=255, blank=True)
    # Reference fields
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_assignments')
    # Additional fields for tracking
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'role', 'key', 'value')
        indexes = [models.Index(fields=['key', 'value'])]

    def match_attribute(self, key, value):
        return self.key == key and self.value == value and self.is_active and not self.is_deleted

    def __str__(self):
        return f"{self.employee} - {self.role} ({self.key}: {self.value})"

