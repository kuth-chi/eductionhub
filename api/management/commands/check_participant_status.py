"""Management command to check participant status for feedback eligibility"""

from django.core.management.base import BaseCommand

from event.models import Event, EventFeedback, EventParticipant
from user.models import User


class Command(BaseCommand):
    """Check participant status for a user and event"""

    help = 'Check if a user can submit feedback for an event'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('event_id', type=int, help='Event ID')

    def handle(self, *args, **options):
        """Execute the command"""
        user_id = options['user_id']
        event_id = options['event_id']

        self.stdout.write(self.style.WARNING(
            f'\n{"=" * 70}'
        ))
        self.stdout.write(self.style.WARNING(
            f'Checking Feedback Eligibility'
        ))
        self.stdout.write(self.style.WARNING(
            f'{"=" * 70}\n'
        ))

        # Check user exists
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(self.style.SUCCESS(
                f'✓ User found: {user.username} ({user.email})'
            ))
            self.stdout.write(f'  - Name: {user.get_full_name()}')
            self.stdout.write(f'  - Active: {user.is_active}')
            self.stdout.write(f'  - Staff: {user.is_staff}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'✗ User with ID {user_id} not found'
            ))
            return

        self.stdout.write('')

        # Check event exists
        try:
            event = Event.objects.get(id=event_id)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Event found: {event.title}'
            ))
            self.stdout.write(f'  - Status: {event.status}')
            self.stdout.write(f'  - Start: {event.start_datetime}')
            self.stdout.write(f'  - Creator: {event.created_by.username}')
        except Event.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'✗ Event with ID {event_id} not found'
            ))
            return

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('-' * 70))
        self.stdout.write('')

        # Check participant records
        participants = EventParticipant.objects.filter(
            user=user,
            event=event
        )

        if not participants.exists():
            self.stdout.write(self.style.ERROR(
                '✗ No participant records found for this user and event'
            ))
            self.stdout.write(
                '\n  Action Required: User needs to register for the event'
            )
            return

        self.stdout.write(self.style.SUCCESS(
            f'✓ Found {participants.count()} participant record(s):\n'
        ))

        valid_statuses = ['registered', 'confirmed', 'attended']
        has_valid_participant = False

        for i, participant in enumerate(participants, 1):
            is_valid = participant.status in valid_statuses
            has_valid_participant = has_valid_participant or is_valid

            status_style = (
                self.style.SUCCESS if is_valid else self.style.ERROR
            )

            self.stdout.write(f'  {i}. Participant ID: {participant.id}')
            self.stdout.write(f'     - Name: {participant.name}')
            self.stdout.write(f'     - Email: {participant.email}')
            self.stdout.write(
                f'     - Status: {status_style(participant.status)}'
            )
            self.stdout.write(
                f'     - Role: {participant.role or "N/A"}'
            )
            self.stdout.write(
                f'     - Registered: {participant.registration_date}'
            )
            self.stdout.write(
                f'     - Valid for feedback: '
                f'{status_style("YES" if is_valid else "NO")}'
            )
            self.stdout.write('')

        self.stdout.write(self.style.WARNING('-' * 70))
        self.stdout.write('')

        # Check for existing feedback
        if has_valid_participant:
            valid_participant = participants.filter(
                status__in=valid_statuses
            ).first()
            existing_feedback = EventFeedback.objects.filter(
                event=event,
                participant=valid_participant
            )

            if existing_feedback.exists():
                feedback = existing_feedback.first()
                self.stdout.write(self.style.WARNING(
                    '⚠ User has already submitted feedback'
                ))
                self.stdout.write(
                    f'  - Feedback ID: {feedback.id}'
                )
                self.stdout.write(
                    f'  - Overall Rating: {feedback.overall_rating}/5'
                )
                self.stdout.write(
                    f'  - Submitted: {feedback.submitted_at}'
                )
                self.stdout.write(
                    f'  - Public: {feedback.is_public}'
                )
                self.stdout.write(
                    '\n  Action: User cannot submit another feedback'
                )
            else:
                self.stdout.write(self.style.SUCCESS(
                    '✓ User is ELIGIBLE to submit feedback'
                ))
                self.stdout.write(
                    '  - Has valid participant status'
                )
                self.stdout.write(
                    '  - No existing feedback found'
                )
        else:
            self.stdout.write(self.style.ERROR(
                '✗ User is NOT ELIGIBLE to submit feedback'
            ))
            self.stdout.write(
                f'\n  Reason: No participant with valid status'
            )
            self.stdout.write(
                f'  Valid statuses: {", ".join(valid_statuses)}'
            )
            self.stdout.write(
                f'\n  Action Required: Contact event organizer to update '
                f'participant status'
            )

        self.stdout.write(self.style.WARNING(
            f'\n{"=" * 70}\n'
        ))
