"""
Quick diagnostic script to check event feedback eligibility.
Run this in Django shell with specific user_id and event_id.

Usage:
    python manage.py shell
    >>> from check_feedback_eligibility import diagnose
    >>> diagnose(user_id=1, event_id=2)
"""

from django.contrib.auth import get_user_model

from event.models import Event, EventFeedback, EventParticipant

User = get_user_model()


def diagnose(user_id, event_id):
    """
    Quick diagnostic for feedback eligibility issues.

    Args:
        user_id: User ID attempting to submit feedback
        event_id: Event ID for feedback
    """
    print("=" * 80)
    print(f"EVENT FEEDBACK ELIGIBILITY CHECK")
    print(f"User ID: {user_id}, Event ID: {event_id}")
    print("=" * 80)

    # Check user
    try:
        user = User.objects.get(id=user_id)
        print(f"✓ User found: {user.username} ({user.email})")
        print(f"  - Is active: {user.is_active}")
        print(f"  - Is staff: {user.is_staff}")
    except User.DoesNotExist:
        print(f"✗ ERROR: User with ID {user_id} not found")
        return

    print()

    # Check event
    try:
        event = Event.objects.get(id=event_id)
        print(f"✓ Event found: {event.title}")
        print(f"  - Status: {event.status}")
        print(f"  - Start: {event.start_datetime}")
        print(f"  - Created by: {event.created_by}")
    except Event.DoesNotExist:
        print(f"✗ ERROR: Event with ID {event_id} not found")
        return

    print()
    print("-" * 80)
    print("PARTICIPANT RECORDS")
    print("-" * 80)

    # Check all participant records
    participants = EventParticipant.objects.filter(event=event, user=user)

    if not participants.exists():
        print(f"✗ NO PARTICIPANT RECORDS FOUND")
        print(
            f"  User {user.username} is NOT registered for event '{event.title}'")
        print()
        print("SOLUTION: User must register for the event first")
        print(f"  - Visit event page and click 'Register'")
        print(f"  - Or create participant record manually in admin")
    else:
        print(f"✓ Found {participants.count()} participant record(s)")
        print()

        for i, p in enumerate(participants, 1):
            print(f"  Participant #{i} (ID: {p.id}):")
            print(f"    - Name: {p.name}")
            print(f"    - Email: {p.email}")
            print(f"    - Status: {p.status}")
            print(f"    - Role: {p.role}")
            print(f"    - Registered: {p.registration_date}")

            # Check if status is valid for feedback
            if p.status in ['registered', 'confirmed', 'attended']:
                print(f"    - ✓ Valid for feedback submission")
            else:
                print(f"    - ✗ INVALID for feedback (status: {p.status})")
                print(f"      Valid statuses: registered, confirmed, attended")
            print()

    print("-" * 80)
    print("EXISTING FEEDBACK")
    print("-" * 80)

    # Check existing feedback
    feedback = EventFeedback.objects.filter(
        event=event,
        participant__user=user
    )

    if not feedback.exists():
        print("✓ No existing feedback - User can submit feedback")
    else:
        print(f"✗ EXISTING FEEDBACK FOUND ({feedback.count()} record(s))")
        for fb in feedback:
            print(f"  - Feedback ID: {fb.id}")
            print(f"  - Rating: {fb.overall_rating}/5")
            print(f"  - Submitted: {fb.submitted_at}")
            print(f"  - Participant: {fb.participant.name}")
        print()
        print("ERROR: User already submitted feedback for this event")

    print()
    print("=" * 80)
    print("ELIGIBILITY SUMMARY")
    print("=" * 80)

    # Determine eligibility
    valid_participant = participants.filter(
        status__in=['registered', 'confirmed', 'attended']
    ).first()

    has_feedback = feedback.exists()

    if not participants.exists():
        print("✗ CANNOT SUBMIT FEEDBACK")
        print("  Reason: Not registered for event")
        print(f"  Action: Register for event '{event.title}'")
    elif not valid_participant:
        print("✗ CANNOT SUBMIT FEEDBACK")
        print(f"  Reason: Invalid participant status")
        print(f"  Current status: {participants.first().status}")
        print("  Required status: registered, confirmed, or attended")
        print("  Action: Contact event organizer to update status")
    elif has_feedback:
        print("✗ CANNOT SUBMIT FEEDBACK")
        print("  Reason: Already submitted feedback")
        print("  Action: Cannot submit duplicate feedback")
    else:
        print("✓ CAN SUBMIT FEEDBACK")
        print(f"  Participant: {valid_participant.name}")
        print(f"  Status: {valid_participant.status}")
        print("  No existing feedback found")

    print("=" * 80)


if __name__ == '__main__':
    print("This script must be run from Django shell:")
    print("  python manage.py shell")
    print("  >>> from check_feedback_eligibility import diagnose")
    print("  >>> diagnose(user_id=1, event_id=2)")
