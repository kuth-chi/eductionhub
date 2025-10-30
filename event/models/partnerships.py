"""
Partnership and impact models.
"""
# pylint: disable=no-member

from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event


class EventPartnership(models.Model):
    """
    Partnerships with other organizations.
    Useful for collaborative events.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='partnerships',
        verbose_name=_("Event")
    )
    partner_organization = models.ForeignKey(
        'organization.Organization',
        on_delete=models.CASCADE,
        related_name='event_partnerships',
        verbose_name=_("Partner organization")
    )
    partnership_type = models.CharField(
        max_length=50,
        verbose_name=_("Partnership type"),
        help_text="E.g., 'Co-host', 'Supporting Partner', 'Media Partner'"
    )
    description = models.TextField(
        blank=True, verbose_name=_("Partnership details"))
    logo = models.ImageField(
        upload_to='events/partners/', null=True, blank=True)

    is_public = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventPartnership model """
        verbose_name = _("Event Partnership")
        verbose_name_plural = _("Event Partnerships")
        ordering = ['event', 'display_order']

    def __str__(self):
        partner_name = self.partner_organization.name
        return (
            f"{partner_name} - {self.partnership_type} ({self.event.title})"
        )


class EventImpact(models.Model):
    """
    Measure and showcase social impact.
    Critical for demonstrating event success and value.
    """
    METRIC_TYPE = [
        ('beneficiaries', _('Beneficiaries Reached')),
        ('funds', _('Funds Raised')),
        ('items', _('Items Distributed')),
        ('volunteers', _('Volunteers Engaged')),
        ('hours', _('Volunteer Hours')),
        ('custom', _('Custom Metric')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='impact_metrics',
        verbose_name=_("Event")
    )
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPE)
    metric_name = models.CharField(
        max_length=100,
        verbose_name=_("Metric name"),
        help_text=(
            "E.g., 'Students helped', 'Books distributed', 'Trees planted'"
        )
    )
    metric_value = models.IntegerField(verbose_name=_("Value"))
    metric_unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g., 'students', 'kg', 'hours'"
    )

    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Icon identifier")

    # Verification
    verified = models.BooleanField(default=False)
    verification_document = models.FileField(
        upload_to='events/impact/',
        null=True,
        blank=True
    )

    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventImpact model """
        verbose_name = _("Event Impact Metric")
        verbose_name_plural = _("Event Impact Metrics")
        ordering = ['event', 'display_order']

    def __str__(self):
        unit = f" {self.metric_unit}" if self.metric_unit else ""
        return (
            f"{self.metric_name}: {self.metric_value}{unit} "
            f"({self.event.title})"
        )
