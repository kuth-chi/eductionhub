import uuid
from django.db import models


class DefaultField(models.Model):
    """Responsible for default fields"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True