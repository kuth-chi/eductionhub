"""
Main Event model: core entity for events with geolocation and financial tracking.
"""
# pylint: disable=no-member

import uuid
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_models import EventType


class Event(models.Model):
    """
    Core event entity: fundraisers, workshops, conferences, charity drives, tournaments, etc.
    Enhanced with precise geolocation for easy discovery and mobile integration.
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('ongoing', _('Ongoing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    VISIBILITY_CHOICES = [
        ('public', _('Public - Anyone can view')),
        ('unlisted', _('Unlisted - Only with link')),
        ('private', _('Private - Invite only')),
    ]

    # Identity
    uuid = models.UUIDField(default=uuid.uuid4, unique=True,
                            editable=False, verbose_name=_("Unique ID"))
    title = models.CharField(max_length=255, verbose_name=_("Event title"))
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name=_("URL slug"))
    description = models.TextField(verbose_name=_("Description"))
    short_description = models.CharField(
        max_length=500, blank=True, help_text="Brief summary for cards/previews")
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name=_("Event type")
    )
    tags = models.JSONField(default=list, blank=True,
                            help_text="Tags for search and filtering")

    # Flexible target: school, organization, or standalone global event
    target_school = models.ForeignKey(
        'schools.School',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
        verbose_name=_("Target school")
    )
    target_organization = models.ForeignKey(
        'organization.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
        verbose_name=_("Target organization")
    )

    # Enhanced Geolocation - Easy to find on maps!
    # Administrative hierarchy (optional, for filtering)
    country = models.ForeignKey(
        'geo.Country',
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name=_("Country")
    )
    state = models.ForeignKey(
        'geo.State',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
        verbose_name=_("State/Province")
    )
    city = models.ForeignKey(
        'geo.City',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
        verbose_name=_("City")
    )
    village = models.ForeignKey(
        'geo.Village',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events',
        verbose_name=_("Village/Suburb")
    )

    # Precise location - KEY FOR USER CONVENIENCE
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Address line 1"),
        help_text="Street address, building name"
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Address line 2"),
        help_text="Apartment, suite, floor, etc."
    )
    postal_code = models.CharField(
        max_length=20, blank=True, verbose_name=_("Postal/ZIP code"))

    # Lat/Lon for maps, distance calculation, and mobile location services
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(
            Decimal('-90')), MaxValueValidator(Decimal('90'))],
        verbose_name=_("Latitude"),
        help_text="Decimal degrees (-90 to 90)"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(
            Decimal('-180')), MaxValueValidator(Decimal('180'))],
        verbose_name=_("Longitude"),
        help_text="Decimal degrees (-180 to 180)"
    )

    # Location display & convenience
    location_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Location name"),
        help_text="E.g., 'City Hall', 'Community Center', 'School Auditorium'"
    )
    location_instructions = models.TextField(
        blank=True,
        verbose_name=_("How to get there"),
        help_text="Directions, parking info, landmarks"
    )
    google_maps_url = models.URLField(
        blank=True, help_text="Direct link to Google Maps")

    # Virtual event option
    is_virtual = models.BooleanField(
        default=False, verbose_name=_("Virtual/Online event"))
    virtual_meeting_url = models.URLField(
        blank=True, help_text="Zoom, Meet, Teams link")
    virtual_meeting_password = models.CharField(max_length=100, blank=True)

    # Timing
    start_datetime = models.DateTimeField(verbose_name=_("Start date & time"))
    end_datetime = models.DateTimeField(verbose_name=_("End date & time"))
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="IANA timezone (e.g., America/New_York)"
    )
    registration_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration opens")
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration closes")
    )

    # Capacity
    max_participants = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Leave empty for unlimited"
    )

    # Media
    banner_image = models.ImageField(
        upload_to='events/banners/',
        null=True,
        blank=True,
        verbose_name=_("Banner image")
    )
    thumbnail_image = models.ImageField(
        upload_to='events/thumbnails/',
        null=True,
        blank=True,
        verbose_name=_("Thumbnail for cards")
    )
    video_url = models.URLField(
        blank=True, verbose_name=_("Promotional video URL"))

    # Financial (for charity/fundraising events)
    funding_goal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("Funding goal")
    )
    current_funding = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("Current funding")
    )
    currency = models.CharField(
        max_length=3, default='USD', verbose_name=_("Currency code"))

    # Status & visibility
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Status")
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name=_("Visibility")
    )
    requires_approval = models.BooleanField(
        default=False,
        help_text="Organizer must approve registrations"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Show on homepage")

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events_created',
        verbose_name=_("Creator")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated at"))
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Published at"))

    # SEO & sharing
    meta_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='events/og/', null=True, blank=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the Event model """
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['status', 'visibility']),
            models.Index(fields=['start_datetime']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['country', 'state', 'city']),
        ]

    def clean(self):
        """Validate event data"""
        super().clean()

        # Date validation
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError({
                    'end_datetime': _('End date must be after start date.')
                })

        # Registration deadline validation
        if self.registration_deadline and self.start_datetime:
            if self.registration_deadline > self.start_datetime:
                raise ValidationError({
                    'registration_deadline': _(
                        'Registration must close before event starts.')
                })

        # Location validation
        if not self.is_virtual:
            if not (self.latitude and self.longitude):
                if not (self.address_line_1 or self.location_name):
                    raise ValidationError(
                        _(
                            'Physical events need either coordinates '
                            '(lat/lon) or an address.'
                        )
                    )

        # Virtual event validation
        if self.is_virtual and not self.virtual_meeting_url:
            raise ValidationError({
                'virtual_meeting_url': _('Virtual events require a meeting URL.')
            })

        # Coordinates validation
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError(
                _('Both latitude and longitude must be provided together.'))

    def save(self, *args, **kwargs):
        """Override save to call full_clean"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    @property
    def is_registration_open(self):
        """Check if registration is currently open"""
        now = timezone.now()

        if self.registration_start and now < self.registration_start:
            return False
        if self.registration_deadline and now > self.registration_deadline:
            return False
        if self.status not in ['published', 'ongoing']:
            return False

        return True

    @property
    def is_full(self):
        """Check if event reached capacity"""
        if not self.max_participants:
            return False
        participant_count = self.participants.filter(
            status='registered').count()
        return participant_count >= self.max_participants

    @property
    def funding_percentage(self):
        """Calculate funding progress"""
        if not self.funding_goal or self.funding_goal == 0:
            return 0
        percentage = (float(self.current_funding) /
                      float(self.funding_goal)) * 100
        return min(100, percentage)

    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city.name if self.city else None,
            self.state.name if self.state else None,
            self.postal_code,
            self.country.name if self.country else None,
        ]
        return ', '.join(filter(None, parts))
