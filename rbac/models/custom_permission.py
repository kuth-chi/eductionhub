# rbac/models/custom_permission.py
from django.contrib.auth.models import Permission
from django.db import models

class CustomPermission(Permission):
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        proxy = True
        verbose_name = 'Custom Permission'
        verbose_name_plural = 'Custom Permissions'