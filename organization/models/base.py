import re
import os
from PIL import Image
import uuid
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _


def organization_logo_image_upload_path(instance, filename):
    """ Generate a file path for new organization logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '',
                  instance.name) or "unnamed-organization"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/organization/logo", filename)


class Industry(models.Model):
    """
    Model representing an industry.
    """
    name = models.CharField(max_length=50)
    created_by = models.CharField(max_length=128, blank=True, db_index=True)
    slug = models.SlugField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    objects = models.Manager()


    def save(self, *args, **kwargs):
        # Ensure slug is created only once if not already set
        if not self.slug:
            self.slug = slugify(
                f"{str(self.name).lower()}-{str(uuid.uuid4())[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.name:
            return self.name
        return "unknown"

    class Meta:
        """
        Meta options for the Industry model.
        """
        ordering = ["-created_at"]
        verbose_name_plural = "Industries"
        verbose_name = "Industry"

class Founder(models.Model):
    """
    Model representing a founder of an organization.
    """
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(default=_("unknown"), max_length=75)
    national_name = models.CharField(default=_("unknown"), max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        name = self.name or ""
        national_name = self.national_name or ""
        if name and not national_name:
            full_name = name
        elif name or national_name:
            full_name = f"{name}({national_name})"
        else:
            full_name = "unknown"
        return str(full_name)
# Create the Organization model
class Organization(models.Model):
    """
    Model representing an organization.
    """
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(max_length=75, blank=True)
    logo = models.ImageField(upload_to=organization_logo_image_upload_path, blank=True, null=True)
    name = models.CharField(max_length=100)
    local_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Local name"))
    description = models.TextField()
    established_year = models.CharField(verbose_name=_("Established year"), max_length=4, null=True, blank=True)
    industries = models.ManyToManyField("Industry", blank=True)
    primary_color = models.CharField(default="000000", max_length=25, verbose_name=_("Primary color"))
    on_primary_color = models.CharField(default="000000", max_length=25, verbose_name=_("on primary color"))

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True)
    founders = models.ManyToManyField(Founder, blank=True, related_name='organizations', verbose_name=_("Founders"))

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{str(self.name).lower()}-{str(uuid.uuid4())[:6]}")

        # Only analyze logo if it exists and primary_color is default
        if self.logo and (not self.primary_color or self.primary_color == "000000"):
            # get path of the image in the storage
            logo_path = self.logo.path if hasattr(self.logo, 'path') else None

            if logo_path and default_storage.exists(logo_path):
                dominant_rgb = get_dominant_color(logo_path)
                self.primary_color = '%02x%02x%02x' % dominant_rgb
                self.on_primary_color = get_contrast_color(dominant_rgb)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("organization-detail", kwargs={"slug": self.slug})

    def delete(self, *args, **kwargs):
        """Override delete to set `is_active` to False instead of deleting."""
        self.is_active = False
        self.save()  # Save the object as inactive before deletion
        return super().delete(*args, **kwargs)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "unknown"
    class Meta:
        """Meta class for the Organization model."""
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["-created_at"]


def get_dominant_color(image_path):
    """Get the dominant color of an image."""
    try:
        with Image.open(image_path) as img:
            img = img.resize((50, 50))
            result = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=1)
            palette = result.getpalette()

            if palette is not None:
                if len(palette) >= 3:
                    dominant_color = tuple(palette[0:3])
                    return dominant_color
                else:
                    # If palette is too small, return black
                    return (0, 0, 0)
            else:
                # If no palette is found, return black
                return (0, 0, 0)
    except FileNotFoundError:
        return (0, 0, 0)
    except Exception:
        return (0, 0, 0)


def get_contrast_color(rgb):
    """Get a contrasting color (black or white) based on the luminance of the RGB color."""
    r, g, b = rgb
    luminance = (0.299*r + 0.587*g + 0.114*b)/255
    return '#000000' if luminance > 0.5 else '#FFFFFF'
