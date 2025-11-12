"""
Debug script to check event feedback submission issues.
Run this in Django shell to diagnose feedback validation problems.
"""

from django.contrib.auth import get_user_model

from event.models import Event, EventFeedback, EventParticipant

User = get_user_model()


def check_feedback_eligibility(user_id, event_id):
    """
    Check if a user can submit feedback for an event.

    Args:
        user_id: User ID
        event_id: Event ID

    Returns:
        dict with eligibility status and details
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"eligible": False, "reason": "User not found"}

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return {"eligible": False, "reason": "Event not found"}

    # Check for participant record
    participants = EventParticipant.objects.filter(
        event=event,
        user=user
    )

    if not participants.exists():
        return {
            "eligible": False,
            "reason": "No participant record found for this user and event",
            "user": str(user),
            "event": str(event),
        }

    participant = participants.first()

    # Check status
    valid_statuses = ['registered', 'confirmed', 'attended']
    if participant.status not in valid_statuses:
        return {
            "eligible": False,
            "reason": f"Participant status '{participant.status}' is not eligible for feedback",
            "participant": str(participant),
            "current_status": participant.status,
            "valid_statuses": valid_statuses,
        }

    # Check for existing feedback
    existing_feedback = EventFeedback.objects.filter(
        event=event,
        participant=participant
    )

    if existing_feedback.exists():
        return {
            "eligible": False,
            "reason": "User has already submitted feedback for this event",
            "participant": str(participant),
            "existing_feedback_id": existing_feedback.first().id,
            "submitted_at": existing_feedback.first().submitted_at,
        }

    return {
        "eligible": True,
        "reason": "User can submit feedback",
        "participant": str(participant),
        "participant_id": participant.id,
        "status": participant.status,
    }


def list_user_event_participations(user_id):
    """List all events a user has registered for."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"error": "User not found"}

    participants = EventParticipant.objects.filter(
        user=user).select_related('event')

    result = []
    for p in participants:
        feedback_submitted = EventFeedback.objects.filter(
            event=p.event,
            participant=p
        ).exists()

        result.append({
            "event_id": p.event.id,
            "event_title": p.event.title,
            "status": p.status,
            "registration_date": p.registration_date,
            "feedback_submitted": feedback_submitted,
            "can_submit_feedback": p.status in ['registered', 'confirmed', 'attended'] and not feedback_submitted,
        })

    return {
        "user": str(user),
        "total_events": len(result),
        "participations": result,
    }


def list_event_participants(event_id):
    """List all participants for an event."""
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return {"error": "Event not found"}

    participants = EventParticipant.objects.filter(
        event=event).select_related('user')

    result = []
    for p in participants:
        feedback_submitted = EventFeedback.objects.filter(
            event=event,
            participant=p
        ).exists()

        result.append({
            "participant_id": p.id,
            "name": p.name,
            "email": p.email,
            "has_user_account": p.user is not None,
            "user_id": p.user.id if p.user else None,
            "status": p.status,
            "registration_date": p.registration_date,
            "feedback_submitted": feedback_submitted,
            "can_submit_feedback": p.user is not None and p.status in ['registered', 'confirmed', 'attended'] and not feedback_submitted,
        })

    return {
        "event": str(event),
        "total_participants": len(result),
        "participants": result,
    }


def check_duplicate_participants(user_id, event_id):
    """Check if there are duplicate participant records (shouldn't happen)."""
    participants = EventParticipant.objects.filter(
        event_id=event_id,
        user_id=user_id
    )

    count = participants.count()

    if count == 0:
        return {"status": "OK", "message": "No participant records found"}
    elif count == 1:
        return {
            "status": "OK",
            "message": "Single participant record found",
            "participant": str(participants.first()),
        }
    else:
        return {
            "status": "ERROR",
            "message": f"Found {count} duplicate participant records!",
            "participants": [str(p) for p in participants],
            "ids": [p.id for p in participants],
        }


# Example usage in Django shell:
# python manage.py shell
# from debug_event_feedback import *
# check_feedback_eligibility(user_id=1, event_id=2)
# list_user_event_participations(user_id=1)
# list_event_participants(event_id=2)
# check_duplicate_participants(user_id=1, event_id=2)

if __name__ == '__main__':
    print("This script should be run in Django shell:")
    print("python manage.py shell")
    print("from debug_event_feedback import *")
    print("check_feedback_eligibility(user_id=1, event_id=2)")
