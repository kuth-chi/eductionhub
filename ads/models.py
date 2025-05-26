# models.py
import os
import re
import uuid
from datetime import date
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

def ad_poster_upload_path(instance, filename):
    """Generate a file path for new ad poster uploads."""
    ext = filename.split('.')[-1]
    title = re.sub(r'[^a-zA-Z0-9_-]', '', instance.campaign_title) or "unnamed-poster"
    filename = f"{title}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/admanager/posters/', filename)

class AdSpace(models.Model):
    """
    Defines where an ad can be placed (e.g., homepage banner, sidebar).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Ad space name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug identifier (e.g. homepage-banner)"))

    def __str__(self):
        return self.name


class AdType(models.Model):
    """
    (Optional) Used to define ad format: image, video, html snippet, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AdManager(models.Model):
    """
    Represents an ad campaign. Can target multiple ad spaces.
    """
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique identifier"))
    campaign_title = models.CharField(max_length=75, verbose_name=_("Campaign title"))
    ad_type = models.ForeignKey(AdType, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.JSONField(default=list, help_text="Tags to match user interest")

    start_datetime = models.DateField(null=True)
    end_datetime = models.DateField(null=True)

    is_active = models.BooleanField(default=True)
    active_ad_period = models.DurationField(null=True, blank=True)
    limited_overdue = models.IntegerField(null=True, blank=True)
    poster = models.ImageField(upload_to=ad_poster_upload_path, null=True, blank=True, help_text="Main image or media for the ad")

    update_datetime = models.DateTimeField(auto_now=True)
    create_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_title


class AdPlacement(models.Model):
    ad = models.ForeignKey('AdManager', on_delete=models.CASCADE, related_name='placements')
    ad_space = models.ForeignKey('AdSpace', on_delete=models.CASCADE, related_name='placements')

    position = models.PositiveIntegerField(default=0, help_text="Order of ad in space")
    is_primary = models.BooleanField(default=False, help_text="Mark if this is the primary ad for space")

    class Meta:
        unique_together = ('ad', 'ad_space')
        ordering = ['position']

    def save(self, *args, **kwargs):
        if not self.position and self.ad_space_id:
            max_position = AdPlacement.objects.filter(ad_space=self.ad_space).aggregate(Max('position'))['position__max'] or 0
            self.position = max_position + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ad.campaign_title} in {self.ad_space.name}"


class UserProfile(models.Model):
    """
    Stores behavioral interest tags for a user.
    """
    user_id = models.CharField(max_length=255, unique=True)
    interests = models.JSONField(default=list)  # e.g. ["tech", "sports"]
    last_active = models.DateTimeField(auto_now=True)


class UserBehavior(models.Model):
    """
    Tracks what users are doing: page visits, categories, etc.
    """
    user_id = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    page_slug = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


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


class AdClick(models.Model):
    """
    Logged when a user clicks an ad.
    """
    ad = models.ForeignKey(AdManager, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    referrer = models.TextField(blank=True)

def normalize_positions(ad_space):
    """
    Reassigns sequential position numbers to AdPlacements in a given AdSpace.
    """
    placements = AdPlacement.objects.filter(ad_space=ad_space).order_by('position')
    for i, placement in enumerate(placements):
        placement.position = i + 1
        placement.save()