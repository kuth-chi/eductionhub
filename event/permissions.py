"""
Event Management Permission Utilities
Centralized permission checking for event-related actions
"""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from event.models import EventOrganizer


class EventPermissionChecker:
    """Utility class for checking event-related permissions"""

    @staticmethod
    def is_event_owner(user, event):
        """Check if user is the event owner (creator)"""
        if not user or not user.is_authenticated:
            return False
        return event.created_by == user

    @staticmethod
    def is_lead_organizer(user, event):
        """Check if user is a lead organizer for the event"""
        if not user or not user.is_authenticated:
            return False
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            role='lead'
        ).exists()

    @staticmethod
    def is_organizer(user, event):
        """Check if user is any type of organizer for the event"""
        if not user or not user.is_authenticated:
            return False
        return EventOrganizer.objects.filter(
            event=event,
            user=user
        ).exists()

    @staticmethod
    def can_edit_event(user, event):
        """Check if user has permission to edit event details"""
        if not user or not user.is_authenticated:
            return False

        # Event owner can always edit
        if EventPermissionChecker.is_event_owner(user, event):
            return True

        # Check if organizer has edit permission
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            can_edit_event=True
        ).exists()

    @staticmethod
    def can_manage_participants(user, event):
        """Check if user can manage participants (approve, check-in, etc.)"""
        if not user or not user.is_authenticated:
            return False

        # Event owner can always manage
        if EventPermissionChecker.is_event_owner(user, event):
            return True

        # Check if organizer has participant management permission
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            can_manage_participants=True
        ).exists()

    @staticmethod
    def can_manage_finances(user, event):
        """Check if user can manage finances (sponsors, expenses)"""
        if not user or not user.is_authenticated:
            return False

        # Event owner can always manage
        if EventPermissionChecker.is_event_owner(user, event):
            return True

        # Check if organizer has finance management permission
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            can_manage_finances=True
        ).exists()

    @staticmethod
    def can_manage_organizers(user, event):
        """Check if user can add/remove organizers"""
        if not user or not user.is_authenticated:
            return False

        # Only event owner or lead organizers can manage team
        return (
            EventPermissionChecker.is_event_owner(user, event) or
            EventPermissionChecker.is_lead_organizer(user, event)
        )

    @staticmethod
    def can_post_updates(user, event):
        """Check if user can post updates/announcements"""
        if not user or not user.is_authenticated:
            return False

        # Event owner can always post
        if EventPermissionChecker.is_event_owner(user, event):
            return True

        # Check if organizer has update posting permission
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            can_post_updates=True
        ).exists()

    @staticmethod
    def can_upload_media(user, event):
        """Check if user can upload photos/media"""
        if not user or not user.is_authenticated:
            return False

        # Event owner can always upload
        if EventPermissionChecker.is_event_owner(user, event):
            return True

        # Check if organizer has media upload permission
        return EventOrganizer.objects.filter(
            event=event,
            user=user,
            can_upload_media=True
        ).exists()

    @staticmethod
    def require_event_owner(user, event):
        """Raise PermissionDenied if user is not the event owner"""
        if not EventPermissionChecker.is_event_owner(user, event):
            raise PermissionDenied(
                "Only the event owner can perform this action")

    @staticmethod
    def require_edit_permission(user, event):
        """Raise PermissionDenied if user cannot edit event"""
        if not EventPermissionChecker.can_edit_event(user, event):
            raise PermissionDenied(
                "You do not have permission to edit this event"
            )

    @staticmethod
    def require_participant_management(user, event):
        """Raise PermissionDenied if user cannot manage participants"""
        if not EventPermissionChecker.can_manage_participants(user, event):
            raise PermissionDenied(
                "You do not have permission to manage participants for this event"
            )

    @staticmethod
    def require_finance_management(user, event):
        """Raise PermissionDenied if user cannot manage finances"""
        if not EventPermissionChecker.can_manage_finances(user, event):
            raise PermissionDenied(
                "You do not have permission to manage finances for this event"
            )

    @staticmethod
    def require_organizer_management(user, event):
        """Raise PermissionDenied if user cannot manage organizers"""
        if not EventPermissionChecker.can_manage_organizers(user, event):
            raise PermissionDenied(
                "Only event owner or lead organizers can manage the team"
            )

    @staticmethod
    def require_update_posting(user, event):
        """Raise PermissionDenied if user cannot post updates"""
        if not EventPermissionChecker.can_post_updates(user, event):
            raise PermissionDenied(
                "You do not have permission to post updates for this event"
            )

    @staticmethod
    def require_media_upload(user, event):
        """Raise PermissionDenied if user cannot upload media"""
        if not EventPermissionChecker.can_upload_media(user, event):
            raise PermissionDenied(
                "You do not have permission to upload media for this event"
            )


def get_user_event_role(user, event):
    """Get user's role in an event"""
    if not user or not user.is_authenticated:
        return None

    if EventPermissionChecker.is_event_owner(user, event):
        return 'owner'
    try:
        organizer = EventOrganizer.objects.get(event=event, user=user)
        return organizer.role
    except ObjectDoesNotExist:
        return None


def get_user_event_permissions(user, event):
    """Get all permissions for a user in an event"""
    if not user or not user.is_authenticated:
        return {}

    permissions = {
        'is_owner': EventPermissionChecker.is_event_owner(user, event),
        'is_lead_organizer': EventPermissionChecker.is_lead_organizer(user, event),
        'is_organizer': EventPermissionChecker.is_organizer(user, event),
        'can_edit_event': EventPermissionChecker.can_edit_event(user, event),
        'can_manage_participants': EventPermissionChecker.can_manage_participants(user, event),
        'can_manage_finances': EventPermissionChecker.can_manage_finances(user, event),
        'can_manage_organizers': EventPermissionChecker.can_manage_organizers(user, event),
        'can_post_updates': EventPermissionChecker.can_post_updates(user, event),
        'can_upload_media': EventPermissionChecker.can_upload_media(user, event),
        'role': get_user_event_role(user, event),
    }

    return permissions
