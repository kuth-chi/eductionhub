import uuid
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models

class EducationalLevel(models.Model):
    uuid = models.UUIDField( unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    level_name = models.CharField(max_length=75, unique=True, verbose_name=_("Level"))
    badge = models.CharField(max_length=125, blank=True, verbose_name=_("badge"))
    color = models.CharField(max_length=6, blank=True, verbose_name=_("color"))
    description = models.CharField(max_length=500, blank=True, default=_("No description"), verbose_name=_("description"))
    
    slug = models.SlugField(max_length=75, null=False, blank=False, verbose_name=_("slug"))
    created_date = models.DateField(auto_now_add=True, verbose_name=_("created at"))
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("status"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("deleted"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.level_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.level_name
    
    class Meta:
        ordering = ("level_name", "-created_date", "updated_date")
        verbose_name = _("education level")
        verbose_name_plural = _("education levels")

class EducationDegree(models.Model):
    uuid = models.UUIDField( unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    degree_name = models.CharField(max_length=75, unique=True, verbose_name=_("Level"))
    badge = models.CharField(max_length=125, blank=True, verbose_name=_("badge"))
    color = models.CharField(max_length=6, blank=True, verbose_name=_("color"))
    description = models.CharField(max_length=500, blank=True, default=_("No description"), verbose_name=_("description"))
    
    slug = models.SlugField(max_length=75, null=False, blank=False, verbose_name=_("slug"))
    created_date = models.DateField(auto_now_add=True, verbose_name=_("created at"))
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("status"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("deleted"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.degree_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.degree_name

    
    class Meta:
        ordering = ("degree_name", "-created_date", "updated_date")
        verbose_name = _("education level")
        verbose_name_plural = _("education levels")