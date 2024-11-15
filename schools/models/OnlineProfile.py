from django.db import models
from django.utils.translation import gettext_lazy as _
from schools.models.base import DefaultField
from schools.models.schoolsModel import School


class Platform(DefaultField):
    """Represents an online platform (e.g., Facebook, Twitter)"""
    name = models.CharField(max_length=128, unique=True)
    url = models.URLField(help_text=_("Base URL of the platform"), blank=True)
    icon = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return str(self.name)


class PlatformProfile(DefaultField):
    """Represents a profile of a school on a specific online platform"""
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="platform_profiles")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="profiles")
    profile_url = models.URLField(help_text=_(
        "URL of the school's profile on the platform"))
    username = models.CharField(max_length=128, blank=True, help_text=_(
        "Username or handle on the platform"))

    def __str__(self):
        return f"{self.school.name} on {self.platform.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'platform'], name='unique_school_platform')
        ]
