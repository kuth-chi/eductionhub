# models.py
import os
import re
import uuid
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _


def ad_poster_upload_path(instance, filename):
    """Generate a file path for new ad poster uploads."""
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    title = re.sub(r'[^a-zA-Z0-9_-]', '',
                   instance.campaign_title or "unnamed") or "unnamed-poster"
    filename = f"{title}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/admanager/posters/', filename)


class AdSpace(models.Model):
    """
    Defines where an ad can be placed (e.g., homepage banner, sidebar).
    """
    name = models.CharField(max_length=100, unique=True,
                            verbose_name=_("Ad space name"))
    slug = models.SlugField(unique=True, verbose_name=_(
        "Slug identifier (e.g. homepage-banner)"))
    objects = models.Manager()

    def __str__(self):
        return self.name


class AdType(models.Model):
    """
    (Optional) Used to define ad format: image, video, html snippet, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


class AdManager(models.Model):
    """
    Represents an ad campaign. Can target multiple ad spaces.
    """
    uuid = models.UUIDField(unique=True, default=uuid.uuid4,
                            verbose_name=_("unique identifier"))
    campaign_title = models.CharField(max_length=75, verbose_name=_("Campaign title"))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Short description"))
    ad_type = models.ForeignKey(
        AdType, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.JSONField(
        default=list, help_text="Tags to match user interest")

    start_datetime = models.DateField(null=True)
    end_datetime = models.DateField(null=True)
    target_url = models.URLField(max_length=500, help_text="URL to navigate to on click", blank=True, null=True, default="")
    is_active = models.BooleanField(default=True)
    active_ad_period = models.DurationField(null=True, blank=True)
    limited_overdue = models.IntegerField(null=True, blank=True)
    poster = models.ImageField(upload_to=ad_poster_upload_path, null=True,
                               blank=True, help_text="Main image or media for the ad")

    update_datetime = models.DateTimeField(auto_now=True)
    create_datetime = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def clean(self):
        """Validate the ad manager instance."""
        super().clean()
        if self.start_datetime and self.end_datetime:
            if self.start_datetime > self.end_datetime:
                raise ValidationError({
                    'end_datetime': _('End date must be after start date.')
                })

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_currently_active(self):
        """Check if the ad is currently active based on date range and status."""
        if not self.is_active:
            return False

        today = date.today()

        # Check if within date range
        if self.start_datetime and today < self.start_datetime:
            return False
        if self.end_datetime and today > self.end_datetime:
            return False

        return True

    def __str__(self):
        return self.campaign_title or ""


class AdPlacement(models.Model):
    ad = models.ForeignKey(
        'ads.AdManager', on_delete=models.CASCADE, related_name='placements')
    ad_space = models.ForeignKey(
        'ads.AdSpace', on_delete=models.CASCADE, related_name='placements')

    position = models.PositiveIntegerField(
        default=0, help_text="Order of ad in space")
    is_primary = models.BooleanField(
        default=False, help_text="Mark if this is the primary ad for space")

    objects = models.Manager()

    class Meta:
        unique_together = ('ad', 'ad_space')
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.position and self.ad_space:
            max_position = AdPlacement.objects.filter(
                ad_space=self.ad_space).aggregate(Max('position'))['position__max'] or 0
            self.position = max_position + 1
        super().save(*args, **kwargs)

    def __str__(self):
        ad_title = str(getattr(self.ad, "campaign_title", "")) if self.ad else ""
        space_name = str(getattr(self.ad_space, "name", "")) if self.ad_space else ""
        return f"{ad_title} in {space_name}"


class UserProfile(models.Model):
    """
    Stores behavioral interest tags for a user.
    """
    user_id = models.CharField(max_length=255, unique=True)
    interests = models.JSONField(default=list)  # e.g. ["tech", "sports"]
    last_active = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class UserBehavior(models.Model):
    """
    Tracks what users are doing: page visits, categories, etc.
    """
    user_id = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    page_slug = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class AdImpression(models.Model):
    """
    Logged when an ad is shown to a user.
    """
    ad = models.ForeignKey(AdManager, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    objects = models.Manager()


class AdClick(models.Model):
    """
    Logged when a user clicks an ad.
    """
    ad = models.ForeignKey(AdManager, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    referrer = models.TextField(blank=True)
    objects = models.Manager()


_NORMALIZING_SPACES = set()


def normalize_positions(ad_space):
    """Reassign sequential position numbers for placements in an ad space.

    Previous implementation called save() per placement which re-fired
    post_save signals causing potential deep recursion. We now:
      1. Guard against re-entrancy with a set of space ids.
      2. Perform a single pass computing desired positions.
      3. Use bulk_update to avoid triggering per-row post_save signals.
    """
    if not ad_space or ad_space.id in _NORMALIZING_SPACES:
        return

    _NORMALIZING_SPACES.add(ad_space.id)
    try:
        placements = list(
            AdPlacement.objects.filter(
                ad_space=ad_space).order_by('position', 'id')
        )
        changed = False
        for i, placement in enumerate(placements, start=1):
            if placement.position != i:
                placement.position = i
                changed = True
        if changed:
            AdPlacement.objects.bulk_update(placements, ['position'])
    finally:
        _NORMALIZING_SPACES.discard(ad_space.id)
