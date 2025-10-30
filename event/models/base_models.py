"""
Base models for event taxonomy: categories and types.
"""
# pylint: disable=no-member

from django.db import models
from django.utils.translation import gettext_lazy as _


class EventCategory(models.Model):
    """
    Flexible event categorization: charity, educational, cultural, sports, health, etc.
    Supports hierarchy for sub-categories.
    """
    name = models.CharField(max_length=100, unique=True,
                            verbose_name=_("Category name"))
    slug = models.SlugField(unique=True, verbose_name=_("URL slug"))
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Icon identifier (e.g., font-awesome class)")
    description = models.TextField(blank=True, verbose_name=_("Description"))
    parent_category = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name=_("Parent category")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventCategory model """
        verbose_name = _("Event Category")
        verbose_name_plural = _("Event Categories")
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class EventType(models.Model):
    """
    Specific event types: fundraiser, workshop, conference, donation-drive,
    school-supply-drive, sports-tournament, health-camp, etc.
    """
    name = models.CharField(max_length=100, verbose_name=_("Type name"))
    slug = models.SlugField(unique=True, verbose_name=_("URL slug"))
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        related_name='event_types',
        verbose_name=_("Category")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventType model """
        verbose_name = _("Event Type")
        verbose_name_plural = _("Event Types")
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
