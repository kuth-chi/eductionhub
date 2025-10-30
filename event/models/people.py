"""
People-related models: organizers and participants.
"""
# pylint: disable=no-member

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event


class EventOrganizer(models.Model):
    """
    Multiple organizers per event with different roles and permissions.
    Supports team-based event management.
    """
    ROLE_CHOICES = [
        ('lead', _('Lead Organizer')),
        ('co-organizer', _('Co-Organizer')),
        ('volunteer-coordinator', _('Volunteer Coordinator')),
        ('finance-manager', _('Finance Manager')),
        ('media-manager', _('Media & Communications')),
        ('logistics', _('Logistics Manager')),
        ('registration', _('Registration Manager')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='organizers',
        verbose_name=_("Event")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name=_("User")
    )
    role = models.CharField(
        max_length=30, choices=ROLE_CHOICES, verbose_name=_("Role"))

    # Granular permissions
    can_edit_event = models.BooleanField(default=False)
    can_manage_participants = models.BooleanField(default=False)
    can_manage_finances = models.BooleanField(default=False)
    can_upload_media = models.BooleanField(default=True)
    can_post_updates = models.BooleanField(default=True)

    notes = models.TextField(
        blank=True, help_text="Internal notes about this organizer")
    added_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventOrganizer model """
        verbose_name = _("Event Organizer")
        verbose_name_plural = _("Event Organizers")
        unique_together = ['event', 'user']
        ordering = ['event', '-role']

    def __str__(self):
        return (
            f"{self.user} - {self.get_role_display()} ({self.event.title})"
        )


class EventParticipant(models.Model):
    """
    Event registration and attendance tracking.
    Supports both registered users and guest registrations.
    """
    PARTICIPANT_STATUS = [
        ('registered', _('Registered')),
        ('waitlist', _('Waitlist')),
        ('confirmed', _('Confirmed')),
        ('attended', _('Attended')),
        ('no-show', _('No Show')),
        ('cancelled', _('Cancelled')),
    ]

    PARTICIPANT_ROLE = [
        ('attendee', _('Attendee')),
        ('speaker', _('Speaker/Presenter')),
        ('volunteer', _('Volunteer')),
        ('staff', _('Staff')),
        ('vip', _('VIP Guest')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_("Event")
    )

    # User account (optional for guest registration)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='event_participations',
        verbose_name=_("User")
    )

    # Guest details (required if no user account)
    name = models.CharField(max_length=255, verbose_name=_("Full name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True,
                             verbose_name=_("Phone number"))

    # Role & status
    role = models.CharField(
        max_length=20,
        choices=PARTICIPANT_ROLE,
        default='attendee',
        verbose_name=_("Role")
    )
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS,
        default='registered',
        verbose_name=_("Status")
    )

    # Additional info
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company, school, or organization"
    )
    special_requirements = models.TextField(
        blank=True,
        help_text="Dietary, accessibility, or other needs"
    )

    # Timestamps
    registration_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # Communication
    registration_confirmed = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)

    notes = models.TextField(blank=True, help_text="Internal notes")

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventParticipant model """
        verbose_name = _("Event Participant")
        verbose_name_plural = _("Event Participants")
        ordering = ['event', 'registration_date']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return (
            f"{self.name} - {self.get_role_display()} ({self.event.title})"
        )
