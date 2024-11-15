import os
from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _

from schools.models.base import DefaultField


class SchoolType(DefaultField):
    """ This class represents a school type """
    type = models.CharField(max_length=128, unique=True,
                            db_index=True, blank=False)
    description = models.TextField(blank=True, default=_('Description about the school type'))
    icon = models.CharField(max_length=128, blank=True,)

    def __str__(self):
        return str(self.type)

    class Meta:
        ordering = ["type"]
        verbose_name = _('School Type')


def school_logo_upload_path(instance, filename):
    """ Generate a file path for new school logo uploads. """
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join('uploads/schools/logos/', filename)




class School(DefaultField):
    """ Represents for School models """
    logo = models.ImageField(blank=True, upload_to=school_logo_upload_path, null=True,)
    name = models.CharField(max_length=75, blank=True)
    local_name = models.CharField(
        max_length=128, blank=True, verbose_name=_('local name'))
    short_name = models.CharField(
        max_length=25, blank=True, verbose_name=_('short name'))
    code = models.CharField(max_length=15, blank=True)
    description = models.TextField(
        blank=True, default=_("The school description"))
    type = models.ManyToManyField(
        "SchoolType", related_name="schools", blank=True)
    established = models.DateField(null=True, blank=True)
    founder = models.CharField(max_length=125, blank=True)
    president = models.CharField(max_length=125, blank=True)
    endowment = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0.00)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name = _("school")
        verbose_name_plural = _("schools")

