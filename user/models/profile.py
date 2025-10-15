import uuid

import pytz
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    photo = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
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
    # NEW FIELDS TO ADD:
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name=_("Phone Number")
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Date of Birth")
    )
    
    # Address fields (Option 1: Simple text)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Address fields (Option 2: Using geo models - RECOMMENDED)
    country = models.ForeignKey(
        'geo.Country', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    state = models.ForeignKey(
        'geo.State', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    city = models.ForeignKey(
        'geo.City', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    # Backwards-compatible aliases for consumers expecting created_at/updated_at
    @property
    def created_at(self):  # noqa: D401
        """Alias for created_date to support clients expecting created_at."""
        return self.created_date

    @property
    def updated_at(self):  # noqa: D401
        """Alias for updated_date to support clients expecting updated_at."""
        return self.updated_date

    def delete(self, *args, **kwargs):
        # Check if the photo field has an associated file
        if self.photo and self.photo.name:
            self.photo.storage.delete(self.photo.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        user_instance = self.user
        user_first_name = (
            user_instance.first_name if getattr(user_instance, "first_name", None) else getattr(user_instance, "username", "")
        )
        user_last_name = getattr(user_instance, "last_name", "")
        user_name = f"{user_first_name} {user_last_name}"
        return user_name
