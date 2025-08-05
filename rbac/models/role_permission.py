# rbac/models/base.py
from django.db import models
from django.contrib.auth.models import Permission
from rbac.models.role import Role

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, blank=True)  # Optional ABAC tag (e.g., context)
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('role', 'permission')
        indexes = [models.Index(fields=['role', 'permission'])]

    def __str__(self):
        return f"{self.role.name} - {self.permission.codename} ({self.key}: {self.value})"