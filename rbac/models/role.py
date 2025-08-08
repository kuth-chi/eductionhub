# rbac/models/role.py
import uuid
from django.db import models
from django.contrib.auth.models import Permission
from organization.models.base import Organization

class Role(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        Permission,
        through="rbac.RolePermission",
        related_name='custom_roles'
    )

    organization = models.ForeignKey(
    Organization, on_delete=models.CASCADE, null=True, blank=True, related_name='roles'
    )


    class Meta:
        ordering = ['created_at']
        unique_together = ('name', 'organization', 'is_active')
    
    def __str__(self):
        return self.name
