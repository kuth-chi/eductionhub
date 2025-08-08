import re, os
from PIL import Image
import colorsys
import io
import uuid
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _

def organization_logo_image_upload_path(instance, filename):
    """ Generate a file path for new organization logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "unnamed-organization"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/organization/logo", filename)

class Industry(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        # Ensure slug is created only once if not already set
        if not self.slug:
            self.slug = slugify(f"{self.name.lower()}-{str(uuid.uuid4())[:6]}")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Industries"
        verbose_name = "Industry"


# Create the Organization model
class Organization(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(max_length=75, blank=True)
    logo = models.ImageField(upload_to=organization_logo_image_upload_path, blank=True, null=True)
    name = models.CharField(max_length=100)
    local_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Local name"))
    description = models.TextField()
    established_year = models.CharField(verbose_name=_("Established year"), max_length=4, null=True, blank=True)
    industry = models.ForeignKey("Industry", on_delete=models.SET_NULL, blank=True, null=True)
    primary_color = models.CharField(default="000000", max_length=25, verbose_name=_("Primary color"))
    on_primary_color = models.CharField(default="000000", max_length=25, verbose_name=_("on primary color"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name.lower()}-{str(uuid.uuid4())[:6]}")

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

    class Meta:
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
    except Exception as e:
        return (0, 0, 0)

def get_contrast_color(rgb):
    # Convert RGB to luminance
    r, g, b = rgb
    luminance = (0.299*r + 0.587*g + 0.114*b)/255
    return '#000000' if luminance > 0.5 else '#FFFFFF'

class Founder(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(default=_("unknown"), max_length=75)
    national_name = models.CharField(default=_("unknown"), max_length=250)

    def __str__(self):
        if self.name and not self.national_name:
            full_name = self.name
        else:
            full_name = self.name + "(" + self.national_name + ")"
        return full_name