"""
    OnlineProfile.py 
    Models
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from schools.models.base import DefaultField
from schools.models.schoolsModel import School


class Platform(models.Model):
    """Represents an online platform (e.g., Facebook, Twitter)"""
    name = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(max_length=5, unique=True, blank=True, verbose_name=_("short name"))
    url = models.URLField(help_text=_("Base URL of the platform"), blank=True)
    icon = models.CharField(max_length=128, blank=True)
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("unique identifier"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("self data field"))

    def __str__(self):
        return str(self.name)


class PlatformProfile(models.Model):
    """Represents a profile of a school on a specific online platform"""
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="platform_profiles_school")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="platform_profiles_platform")
    profile_url = models.URLField(blank=True, help_text=_(
        "URL of the school's profile on the platform"))
    username = models.CharField(max_length=128, blank=True, help_text=_(
        "Username or handle on the platform"))
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.school.name} on {self.platform.name}"

    class Meta:
        verbose_name = _("platform profile")
        verbose_name_plural = _("platform profiles")
        indexes = [
            models.Index(fields=['school', 'platform'], name='school_platform_idx'),
        ]
