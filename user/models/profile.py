import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
import pytz

from django.conf import settings


def user_directory_path(instance, filename):
    """Generate file path for new profile image"""
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"user_{instance.user.username}/{filename}"


class Profile(models.Model):
    """Create profile model instance django user model"""

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE
    )
    photo = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    GENDER_CHOICES = [
        ("FEMALE", _("Female")),
        ("MALE", _("Male")),
        ("OTHER", _("Other")),
    ]
    gender = models.CharField(max_length=6, blank=True, choices=GENDER_CHOICES)
    occupation = models.CharField(max_length=75, default="untitled")
    timezone = models.CharField(
        max_length=100, choices=[(tz, tz) for tz in pytz.all_timezones], default="UTC"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def delete(self, *args, **kwargs):
        # Check if the photo field has an associated file
        if self.photo and self.photo.name:
            self.photo.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        user_first_name = (
            self.user.first_name if self.user.first_name else self.user.username
        )
        user_last_name = self.user.last_name if self.user.last_name else ""
        user_name = f"{user_first_name} {user_last_name}"
        return user_name
