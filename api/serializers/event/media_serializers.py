"""Media and documentation serializers"""

from rest_framework import serializers

from event.models import EventFeedback, EventMilestone, EventPhoto, EventUpdate


class EventPhotoSerializer(serializers.ModelSerializer):
    """Event photo gallery"""
    photographer_name = serializers.SerializerMethodField()

    class Meta:
        """Meta information for the EventPhotoSerializer"""
        model = EventPhoto
        fields = [
            'id', 'event', 'image', 'caption', 'photographer',
            'photographer_name', 'photographer_credit', 'taken_at',
            'tags', 'is_featured', 'is_public', 'display_order',
            'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']

    def get_photographer_name(self, obj):
        """Get full name of photographer if user is linked"""
        if obj.photographer:
            return obj.photographer.get_full_name()
        return obj.photographer_credit or 'Unknown'


class EventUpdateSerializer(serializers.ModelSerializer):
    """Event updates and announcements"""
    posted_by_name = serializers.CharField(
        source='posted_by.get_full_name',
        read_only=True
    )

    class Meta:
        """Meta information for the EventUpdateSerializer"""
        model = EventUpdate
        fields = [
            'id', 'event', 'update_type', 'title', 'content',
            'image', 'posted_by', 'posted_by_name', 'posted_at',
            'is_pinned', 'is_public', 'notify_participants',
            'notify_sponsors'
        ]
        read_only_fields = ['posted_by', 'posted_at']

    def create(self, validated_data):
        """Set posted_by to current user"""
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class EventMilestoneSerializer(serializers.ModelSerializer):
    """Event milestones and achievements"""

    class Meta:
        """Meta information for the EventMilestoneSerializer"""
        model = EventMilestone
        fields = [
            'id', 'event', 'title', 'description', 'target_date',
            'completion_date', 'is_completed', 'proof_image',
            'proof_document', 'completion_notes', 'display_order',
            'created_at'
        ]
        read_only_fields = ['created_at']


class EventFeedbackSerializer(serializers.ModelSerializer):
    """Event feedback and ratings"""
    participant_name = serializers.CharField(
        source='participant.name',
        read_only=True
    )
    participant_user_id = serializers.IntegerField(
        source='participant.user.id',
        read_only=True,
        allow_null=True
    )

    class Meta:
        """Meta information for the EventFeedbackSerializer"""
        model = EventFeedback
        fields = [
            'id', 'event', 'participant', 'participant_name', 'participant_user_id',
            'overall_rating', 'organization_rating', 'content_rating',
            'venue_rating', 'comment', 'what_went_well',
            'what_to_improve', 'would_recommend', 'is_public',
            'is_featured', 'submitted_at'
        ]
        read_only_fields = ['submitted_at']

    def validate(self, attrs):
        """Ensure participant is registered for the event"""
        participant = attrs['participant']
        if participant.status not in ['registered', 'confirmed', 'attended']:
            raise serializers.ValidationError(
                'Only registered participants can provide feedback'
            )
        return attrs


class EventFeedbackCreateSerializer(serializers.ModelSerializer):
    """Simplified feedback creation"""

    class Meta:
        """Meta information for the EventFeedbackCreateSerializer"""
        model = EventFeedback
        fields = [
            'event', 'overall_rating', 'organization_rating',
            'content_rating', 'venue_rating', 'comment',
            'what_went_well', 'what_to_improve', 'would_recommend',
            'is_public'
        ]

    def validate(self, attrs):
        """Validate event and check for existing feedback"""
        user = self.context['request'].user
        event = attrs['event']

        # Check if user has already submitted feedback for this event
        from event.models import EventParticipant

        participant = EventParticipant.objects.filter(
            event=event,
            user=user,
            status__in=['registered', 'confirmed', 'attended']
        ).first()

        if participant and EventFeedback.objects.filter(
            event=event,
            participant=participant
        ).exists():
            raise serializers.ValidationError(
                'You have already submitted feedback for this event'
            )

        return attrs

    def create(self, validated_data):
        """Link to participant record"""
        import logging

        from event.models import EventParticipant

        logger = logging.getLogger(__name__)
        user = self.context['request'].user
        event = validated_data['event']

        # Debug logging
        logger.info(
            f"Feedback submission attempt - User: {user.id}, Event: {event.id}")

        # Check all participant records for debugging
        all_participants = EventParticipant.objects.filter(
            event=event, user=user)
        logger.info(
            f"Found {all_participants.count()} participant records for user {user.id} in event {event.id}")
        for p in all_participants:
            logger.info(
                f"  - Participant {p.id}: status={p.status}, name={p.name}, email={p.email}")

        # Find participant record
        # Allow feedback from registered, confirmed, or attended participants
        try:
            participant = EventParticipant.objects.get(
                event=event,
                user=user,
                status__in=['registered', 'confirmed', 'attended']
            )
            validated_data['participant'] = participant
            logger.info(
                f"Using participant {participant.id} with status {participant.status}")
        except EventParticipant.DoesNotExist as exc:
            # Check if participant exists with different status
            participant_with_other_status = EventParticipant.objects.filter(
                event=event,
                user=user
            ).first()

            if participant_with_other_status:
                logger.warning(
                    f"Participant exists but has invalid status: {participant_with_other_status.status}"
                )
                raise serializers.ValidationError(
                    f'You cannot provide feedback with status "{participant_with_other_status.status}". '
                    'Only registered, confirmed, or attended participants can provide feedback.'
                ) from exc
            else:
                logger.warning(
                    f"No participant record found for user {user.id} in event {event.id}")
                raise serializers.ValidationError(
                    'You must be registered for this event to provide feedback. '
                    'Please register for the event first.'
                ) from exc
        except EventParticipant.MultipleObjectsReturned:
            # If multiple participant records exist (shouldn't happen due to unique_together),
            # use the first one with valid status
            logger.warning(
                f"Multiple participant records found for user {user.id} in event {event.id}"
            )
            participant = EventParticipant.objects.filter(
                event=event,
                user=user,
                status__in=['registered', 'confirmed', 'attended']
            ).first()
            if not participant:
                raise serializers.ValidationError(
                    'You must be registered for this event to provide feedback'
                )
            validated_data['participant'] = participant
            logger.info(f"Using first valid participant {participant.id}")

        return super().create(validated_data)


class EventFeedbackSummarySerializer(serializers.Serializer):
    """Aggregate feedback statistics"""
    average_overall = serializers.FloatField()
    average_organization = serializers.FloatField()
    average_content = serializers.FloatField()
    average_venue = serializers.FloatField()
    total_responses = serializers.IntegerField()
    recommend_percentage = serializers.FloatField()
    rating_distribution = serializers.DictField()

    def create(self, validated_data):
        """Not used for read-only serializer"""
        raise NotImplementedError()

    def update(self, instance, validated_data):
        """Not used for read-only serializer"""
        raise NotImplementedError()
