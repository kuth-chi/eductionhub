"""
Content models: photos, updates, milestones, and feedback.
"""
# pylint: disable=no-member

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event
from .people import EventParticipant


class EventPhoto(models.Model):
    """
    Photo gallery for event documentation.
    Essential for transparency and showcasing impact.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_("Event")
    )
    image = models.ImageField(
        upload_to='events/photos/', verbose_name=_("Photo"))
    caption = models.CharField(
        max_length=500, blank=True, verbose_name=_("Caption"))

    # Photo metadata
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='event_photos',
        verbose_name=_("Photographer")
    )
    photographer_credit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Photographer name if not a user"
    )
    taken_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Photo taken at")
    )

    # Organization
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags: ceremony, distribution, students, volunteers, etc."
    )

    # Display settings
    is_featured = models.BooleanField(
        default=False, help_text="Show in highlights")
    is_public = models.BooleanField(
        default=True, help_text="Visible to public")
    display_order = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventPhoto model """
        verbose_name = _("Event Photo")
        verbose_name_plural = _("Event Photos")
        ordering = ['event', 'display_order', '-taken_at']

    def __str__(self):
        return f"Photo for {self.event.title} - {self.uploaded_at.date()}"


class EventUpdate(models.Model):
    """
    Progress updates and announcements for stakeholders.
    Keeps sponsors, participants, and community informed.
    """
    UPDATE_TYPE = [
        ('general', _('General Update')),
        ('milestone', _('Milestone Achieved')),
        ('announcement', _('Announcement')),
        ('reminder', _('Reminder')),
        ('thank-you', _('Thank You')),
        ('urgent', _('Urgent Notice')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name=_("Event")
    )
    update_type = models.CharField(
        max_length=20,
        choices=UPDATE_TYPE,
        default='general',
        verbose_name=_("Update type")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))

    # Media attachment
    image = models.ImageField(
        upload_to='events/updates/', null=True, blank=True)

    # Posting details
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_updates',
        verbose_name=_("Posted by")
    )
    posted_at = models.DateTimeField(auto_now_add=True)

    # Display settings
    is_pinned = models.BooleanField(
        default=False, help_text="Pin to top of updates")
    is_public = models.BooleanField(default=True)

    # Notifications
    notify_participants = models.BooleanField(default=False)
    notify_sponsors = models.BooleanField(default=False)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventUpdate model """
        verbose_name = _("Event Update")
        verbose_name_plural = _("Event Updates")
        ordering = ['event', '-is_pinned', '-posted_at']

    def __str__(self):
        return f"{self.title} - {self.event.title}"


class EventMilestone(models.Model):
    """
    Track key achievements and goals.
    Great for fundraising campaigns and progress visualization.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_("Event")
    )
    title = models.CharField(
        max_length=255, verbose_name=_("Milestone title"))
    description = models.TextField(verbose_name=_("Description"))

    # Target & completion
    target_date = models.DateField(verbose_name=_("Target date"))
    completion_date = models.DateField(
        null=True, blank=True, verbose_name=_("Completion date"))
    is_completed = models.BooleanField(
        default=False, verbose_name=_("Completed"))

    # Proof/evidence
    proof_image = models.ImageField(
        upload_to='events/milestones/',
        null=True,
        blank=True,
        verbose_name=_("Proof image")
    )
    proof_document = models.FileField(
        upload_to='events/milestones/docs/',
        null=True,
        blank=True,
        verbose_name=_("Proof document")
    )
    completion_notes = models.TextField(blank=True)

    # Display
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventMilestone model """
        verbose_name = _("Event Milestone")
        verbose_name_plural = _("Event Milestones")
        ordering = ['event', 'display_order', 'target_date']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.title} - {self.event.title}"


class EventFeedback(models.Model):
    """
    Post-event feedback and ratings.
    Helps improve future events and build credibility.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name=_("Event")
    )
    participant = models.ForeignKey(
        EventParticipant,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name=_("Participant")
    )

    # Ratings (1-5 stars)
    overall_rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        verbose_name=_("Overall rating")
    )
    organization_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="How well organized was the event?"
    )
    content_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Quality of content/activities"
    )
    venue_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Venue and facilities"
    )

    # Feedback
    comment = models.TextField(blank=True, verbose_name=_("Comments"))
    what_went_well = models.TextField(blank=True)
    what_to_improve = models.TextField(blank=True)
    would_recommend = models.BooleanField(
        null=True, help_text="Would you recommend this event?")

    # Display settings
    is_public = models.BooleanField(
        default=True,
        help_text="Allow others to see this feedback"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Feature as testimonial")

    submitted_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventFeedback model """
        verbose_name = _("Event Feedback")
        verbose_name_plural = _("Event Feedback")
        ordering = ['event', '-submitted_at']
        unique_together = ['event', 'participant']

    def __str__(self):
        participant_name = self.participant.name
        return (
            f"Feedback from {participant_name} - {self.overall_rating}★"
        )
