import os
import re
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from schools.models.base import DefaultField

class SchoolType(DefaultField):
    """ This class represents a school type """
    type = models.CharField(max_length=128, unique=True,
                            db_index=True, blank=False)
    description = models.TextField(
        blank=True, default=_('Description about the school type'))
    icon = models.CharField(max_length=128, blank=True,)

    def __str__(self):
        return str(self.type)

    class Meta:
        ordering = ["type"]
        verbose_name = _('School Type')

def school_logo_upload_path(instance, filename):
    """ Generate a file path for new school logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/schools/logos/', filename)

def school_cover_image_upload_path(instance, filename):
    """ Generate a file path for new school logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/schools/cover/', filename)


class School(models.Model):
    """ Represents for School models """
    logo = models.ImageField(
        blank=True, upload_to=school_logo_upload_path, null=True, verbose_name=_('logo'))
    cover_image = models.ImageField(upload_to=school_cover_image_upload_path, blank=True, null=True, verbose_name=_('cover image'))
    name = models.CharField(max_length=75, blank=True, verbose_name=_('name'))
    local_name = models.CharField(
        max_length=128, blank=True, verbose_name=_('local name'))
    short_name = models.CharField(
        max_length=25, blank=True, verbose_name=_('short name'))
    code = models.CharField(max_length=15, blank=True, verbose_name=_('code'))
    description = models.TextField(
        blank=True, default=_("The school description"))
    established = models.DateField(
        null=True, blank=True, verbose_name=_('established'))
    founder = models.CharField(
        max_length=125, blank=True, verbose_name=_('founder'))
    president = models.CharField(
        max_length=125, blank=True, verbose_name=_('president'))
    endowment = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, default=0.00, verbose_name=_('endowment'))
    location = models.CharField(
        max_length=255, blank=True, verbose_name=_('location'))
    motto = models.CharField(max_length=250, blank=True, verbose_name=_('motto'), default=_('N/A'))	
    tuition = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0.00, verbose_name=(_("tuition")))
    
    # References
    type = models.ManyToManyField("SchoolType", related_name="school_types", blank=True, verbose_name=_('type'))
    platforms = models.ManyToManyField("Platform", related_name="school_platforms", through="PlatformProfile", verbose_name=_('platforms'))
    educational_levels = models.ManyToManyField("EducationalLevel", related_name="school_educational_levels", blank=True, verbose_name=_("school level"))
    
    # Tracking Fields
    slug = models.SlugField(max_length=75, blank=True, verbose_name=_('slug'))
    uuid = models.URLField(unique=True, default=uuid.uuid4, verbose_name=_("unique identifier"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("self data field"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + (str(uuid.uuid4())[:6])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name) or _("Unnamed School")

    class Meta:
        ''' Meta class used to handle UI and configuration '''
        ordering = ['name']
        verbose_name = _("school")
        verbose_name_plural = _("schools")

