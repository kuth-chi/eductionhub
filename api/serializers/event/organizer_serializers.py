"""Organizer and partnership serializers"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from event.models import Event, EventImpact, EventOrganizer, EventPartnership

User = get_user_model()


class EventOrganizerSerializer(serializers.ModelSerializer):
    """Event organizer details with user information"""
    user_name = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_avatar = serializers.SerializerMethodField(read_only=True)
    role_display = serializers.CharField(
        source='get_role_display', read_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Event organizer configuration"""
        model = EventOrganizer
        fields = [
            'id', 'event', 'user', 'user_name', 'user_email', 'user_avatar',
            'role', 'role_display', 'can_edit_event', 'can_manage_participants',
            'can_manage_finances', 'can_upload_media',
            'can_post_updates', 'notes', 'added_at'
        ]
        read_only_fields = ['added_at']

    def get_user_name(self, obj):
        """Get full name or email"""
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.email

    def get_user_avatar(self, obj):
        """Get user avatar URL if available"""
        if hasattr(obj.user, 'profile') and obj.user.profile.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.photo.url)
        return None

    def validate(self, attrs):
        """Validate organizer data"""
        # Check for duplicate organizer
        event = attrs.get('event')
        user = attrs.get('user')

        if event and user:
            # For updates, exclude current instance
            queryset = EventOrganizer.objects.filter(event=event, user=user)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    'This user is already an organizer for this event'
                )

        # Validate permissions based on role
        role = attrs.get('role', self.instance.role if self.instance else None)
        if role == 'lead':
            # Lead organizers should have most permissions
            attrs.setdefault('can_edit_event', True)
            attrs.setdefault('can_manage_participants', True)
            attrs.setdefault('can_manage_finances', True)
            attrs.setdefault('can_upload_media', True)
            attrs.setdefault('can_post_updates', True)

        return attrs


class EventOrganizerCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding new organizers"""
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """Create organizer configuration"""
        model = EventOrganizer
        fields = [
            'event', 'user', 'user_email', 'role',
            'can_edit_event', 'can_manage_participants',
            'can_manage_finances', 'can_upload_media',
            'can_post_updates', 'notes'
        ]

    def validate(self, attrs):
        """Validate and resolve user from email if provided"""
        user_email = attrs.pop('user_email', None)

        if user_email and not attrs.get('user'):
            try:
                user = User.objects.get(email=user_email)
                attrs['user'] = user
            except User.DoesNotExist as exc:
                raise serializers.ValidationError({
                    'user_email': 'No user found with this email address'
                }) from exc

        if not attrs.get('user'):
            raise serializers.ValidationError({
                'user': 'Either user ID or user_email must be provided'
            })

        # Check for duplicate
        event = attrs['event']
        user = attrs['user']
        if EventOrganizer.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError(
                'This user is already an organizer for this event'
            )

        # Set default permissions based on role
        role = attrs.get('role', 'co-organizer')
        if role == 'lead':
            attrs.setdefault('can_edit_event', True)
            attrs.setdefault('can_manage_participants', True)
            attrs.setdefault('can_manage_finances', True)
        elif role == 'finance-manager':
            attrs.setdefault('can_manage_finances', True)
        elif role == 'registration':
            attrs.setdefault('can_manage_participants', True)

        return attrs


class EventOrganizerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating organizer permissions"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Update organizer configuration"""
        model = EventOrganizer
        fields = [
            'role', 'can_edit_event', 'can_manage_participants',
            'can_manage_finances', 'can_upload_media',
            'can_post_updates', 'notes'
        ]


class EventOrganizerInviteSerializer(serializers.Serializer):
    """Invite user as event organizer"""
    event_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=EventOrganizer.ROLE_CHOICES)
    can_edit_event = serializers.BooleanField(default=False)
    can_manage_participants = serializers.BooleanField(default=False)
    can_manage_finances = serializers.BooleanField(default=False)
    can_upload_media = serializers.BooleanField(default=True)
    can_post_updates = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_user_email(self, value):
        """Check if user exists"""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                'User with this email does not exist'
            ) from exc
        return value

    def validate(self, attrs):
        """Validate event and check for duplicates"""
        try:
            event = Event.objects.get(id=attrs['event_id'])
        except Event.DoesNotExist as exc:  # pylint: disable=no-member
            raise serializers.ValidationError({
                'event_id': 'Event not found'
            }) from exc

        user = User.objects.get(email=attrs['user_email'])

        if EventOrganizer.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError(
                'This user is already an organizer for this event'
            )

        attrs['event'] = event
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        """Create event organizer from invitation data"""
        event = validated_data.pop('event')
        user = validated_data.pop('user')
        validated_data.pop('event_id')
        validated_data.pop('user_email')

        organizer = EventOrganizer.objects.create(
            event=event,
            user=user,
            **validated_data
        )
        return organizer

    def update(self, instance, validated_data):
        """Update is not supported for invitations"""
        raise NotImplementedError(
            'Use EventOrganizerUpdateSerializer for updates')


class EventPartnershipSerializer(serializers.ModelSerializer):
    """Event partnership details with organization information"""
    partner_name = serializers.CharField(
        source='partner_organization.name',
        read_only=True
    )
    partner_logo = serializers.SerializerMethodField(read_only=True)
    partnership_type_display = serializers.CharField(
        source='partnership_type',
        read_only=True
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Partnership configuration"""
        model = EventPartnership
        fields = [
            'id', 'event', 'partner_organization', 'partner_name',
            'partner_logo', 'partnership_type', 'partnership_type_display',
            'description', 'logo', 'is_public', 'display_order', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_partner_logo(self, obj):
        """Get partner organization logo URL"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
        elif obj.partner_organization and obj.partner_organization.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.partner_organization.logo.url)
        return None

    def validate(self, attrs):
        """Validate partnership data"""
        event = attrs.get('event')
        partner_org = attrs.get('partner_organization')

        if event and partner_org:
            # Check for duplicate partnership
            queryset = EventPartnership.objects.filter(
                event=event,
                partner_organization=partner_org
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    'This organization is already a partner for this event'
                )

        return attrs


class EventPartnershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating partnerships"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Create partnership configuration"""
        model = EventPartnership
        fields = [
            'event', 'partner_organization', 'partnership_type',
            'description', 'logo', 'is_public', 'display_order'
        ]

    def validate(self, attrs):
        """Validate new partnership"""
        event = attrs['event']
        partner_org = attrs['partner_organization']

        if EventPartnership.objects.filter(
            event=event,
            partner_organization=partner_org
        ).exists():
            raise serializers.ValidationError(
                'This organization is already a partner for this event'
            )

        return attrs


class EventImpactSerializer(serializers.ModelSerializer):
    """Event impact metrics with validation"""
    metric_type_display = serializers.CharField(
        source='get_metric_type_display',
        read_only=True
    )
    verification_document_url = serializers.SerializerMethodField(
        read_only=True)

    class Meta:  # pylint: disable=too-few-public-methods
        """Impact metric configuration"""
        model = EventImpact
        fields = [
            'id', 'event', 'metric_type', 'metric_type_display',
            'metric_name', 'metric_value', 'metric_unit', 'description',
            'icon', 'verified', 'verification_document',
            'verification_document_url', 'display_order', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_verification_document_url(self, obj):
        """Get verification document URL if available"""
        if obj.verification_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.verification_document.url)
        return None

    def validate_metric_value(self, value):
        """Validate metric value is positive"""
        if value < 0:
            raise serializers.ValidationError('Metric value must be positive')
        return value

    def validate(self, attrs):
        """Validate impact metric data"""
        # If verified, should have verification document
        verified = attrs.get('verified', False)
        verification_doc = attrs.get('verification_document')

        if verified and not verification_doc and not (
            self.instance and self.instance.verification_document
        ):
            raise serializers.ValidationError({
                'verification_document': 'Verification document is required for verified metrics'
            })

        return attrs


class EventImpactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating impact metrics"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Create impact metric configuration"""
        model = EventImpact
        fields = [
            'event', 'metric_type', 'metric_name', 'metric_value',
            'metric_unit', 'description', 'icon', 'verified',
            'verification_document', 'display_order'
        ]

    def validate_metric_value(self, value):
        """Validate metric value is positive"""
        if value < 0:
            raise serializers.ValidationError('Metric value must be positive')
        return value


class EventImpactSummarySerializer(serializers.Serializer):
    """Aggregate impact across events"""
    total_events = serializers.IntegerField(read_only=True)
    total_beneficiaries = serializers.IntegerField(read_only=True)
    total_funds_raised = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_volunteers = serializers.IntegerField(read_only=True)
    total_volunteer_hours = serializers.IntegerField(read_only=True)
    custom_metrics = serializers.DictField(read_only=True)

    def create(self, validated_data):
        """Not implemented - read-only serializer"""
        raise NotImplementedError('EventImpactSummarySerializer is read-only')

    def update(self, instance, validated_data):
        """Not implemented - read-only serializer"""
        raise NotImplementedError('EventImpactSummarySerializer is read-only')
