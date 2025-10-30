"""Participant and registration serializers"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from event.models import EventParticipant


class EventParticipantSerializer(serializers.ModelSerializer):
    """Full participant details for organizers"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Full participant details for organizers"""
        model = EventParticipant
        fields = [
            'id', 'event', 'event_title', 'user', 'user_email',
            'name', 'email', 'phone', 'role', 'status',
            'organization_name', 'special_requirements',
            'registration_date', 'confirmation_date',
            'check_in_time', 'check_out_time',
            'registration_confirmed', 'reminder_sent', 'notes'
        ]
        read_only_fields = [
            'registration_date', 'check_in_time', 'check_out_time'
        ]


class EventParticipantCreateSerializer(serializers.ModelSerializer):
    """Serializer for event registration"""
    ticket = serializers.IntegerField(required=False, write_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """ Fields for participant registration """
        model = EventParticipant
        fields = [
            'event', 'name', 'email', 'phone',
            'organization_name', 'special_requirements', 'ticket'
        ]

    def validate(self, attrs):
        """Check if event is open and has capacity"""
        from event.models import \
            EventTicket  # Import here to avoid circular import

        event = attrs['event']

        # Check if registration is open
        if not event.is_registration_open:
            raise serializers.ValidationError(
                'Registration is not currently open for this event'
            )

        # Validate ticket if provided
        ticket_id = attrs.pop('ticket', None)
        if ticket_id:
            try:
                ticket = EventTicket.objects.get(id=ticket_id, event=event)
                if not ticket.is_available:
                    raise serializers.ValidationError(
                        f'Ticket "{ticket.name}" is not available for purchase'
                    )
                attrs['_ticket'] = ticket  # Store for create method
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError(
                    'Invalid ticket selected'
                ) from exc

        # Check capacity
        if event.is_full:
            # Auto-add to waitlist
            attrs['status'] = 'waitlist'
        else:
            attrs['status'] = 'registered'

        # Check for duplicate registration
        email = attrs['email']
        if EventParticipant.objects.filter(event=event, email=email).exists():
            raise serializers.ValidationError(
                'You have already registered for this event'
            )

        return attrs

    def create(self, validated_data):
        """Create participant and link user if authenticated"""
        from django.db import transaction

        # Extract ticket if provided
        ticket = validated_data.pop('_ticket', None)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            # Auto-fill from user profile if not provided
            if not validated_data.get('name'):
                validated_data['name'] = request.user.get_full_name(
                ) or request.user.email

        # Use transaction to ensure ticket quantity is updated atomically
        with transaction.atomic():
            participant = super().create(validated_data)

            # Update ticket quantity_sold if ticket was selected
            if ticket:
                ticket.quantity_sold += 1
                ticket.save(update_fields=['quantity_sold'])

            return participant


class EventParticipantCheckInSerializer(serializers.Serializer):
    """Serializer for checking in participants"""
    participant_id = serializers.IntegerField()
    check_in = serializers.BooleanField(default=True)

    def validate_participant_id(self, value):
        """Ensure participant exists"""
        try:
            EventParticipant.objects.get(id=value)
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError('Participant not found') from exc
        return value

    def create(self, validated_data):
        """Update participant check-in status"""
        participant = EventParticipant.objects.get(
            id=validated_data['participant_id']
        )

        if validated_data['check_in']:
            participant.status = 'attended'
            participant.check_in_time = timezone.now()
        else:
            participant.check_out_time = timezone.now()

        participant.save()
        return participant

    def update(self, instance, validated_data):
        """Not implemented for check-in serializer"""
        raise NotImplementedError('Use create() for check-in operations')


class EventParticipantPublicSerializer(serializers.ModelSerializer):
    """Public participant list (privacy-focused)"""

    class Meta:  # pylint: disable=too-few-public-methods
        """ Public participant list (privacy-focused) """
        model = EventParticipant
        fields = ['name', 'role', 'organization_name']
