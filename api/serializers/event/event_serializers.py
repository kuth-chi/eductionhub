"""Core event serializers with geolocation support"""

from django.db.models import Avg
from rest_framework import serializers

from api.serializers.organizations.organization_serializers import \
    OrganizationSerializer
from api.serializers.schools.locations import (CitySerializer,
                                               CountrySerializer,
                                               StateSerializer,
                                               VillageSerializer)
from api.serializers.schools.test import SimpleSchoolSerializer
from event.models import Event, EventCategory, EventType

from .financial_serializers import (EventSponsorSerializer,
                                    EventTicketSerializer)
from .media_serializers import (EventMilestoneSerializer, EventPhotoSerializer,
                                EventUpdateSerializer)
from .organizer_serializers import (EventImpactSerializer,
                                    EventOrganizerSerializer)


class EventCategorySerializer(serializers.ModelSerializer):
    """Event category with hierarchy support"""
    subcategories = serializers.SerializerMethodField()

    class Meta:
        """Meta information for the EventCategorySerializer"""
        model = EventCategory
        fields = [
            'id', 'name', 'slug', 'icon', 'description',
            'parent_category', 'subcategories', 'is_active', 'created_at'
        ]

    def get_subcategories(self, obj):
        """Get active subcategories"""
        if obj.subcategories.exists():
            return EventCategorySerializer(
                obj.subcategories.filter(is_active=True),
                many=True,
                context=self.context
            ).data
        return []


class EventTypeSerializer(serializers.ModelSerializer):
    """Event type serializer"""
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    category_slug = serializers.CharField(
        source='category.slug', read_only=True)

    class Meta:
        """Meta information for the EventTypeSerializer"""
        model = EventType
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'category_slug', 'description', 'icon', 'is_active'
        ]


class EventLocationSerializer(serializers.Serializer):
    """Structured location data with lat/lon for easy map integration"""
    # Administrative hierarchy
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    village = VillageSerializer(read_only=True)

    # Precise location
    address_line_1 = serializers.CharField()
    address_line_2 = serializers.CharField()
    postal_code = serializers.CharField()
    full_address = serializers.CharField(read_only=True)

    # Coordinates for maps
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, allow_null=True)
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, allow_null=True)

    # Display info
    location_name = serializers.CharField()
    location_instructions = serializers.CharField()
    google_maps_url = serializers.URLField()

    # Virtual event
    is_virtual = serializers.BooleanField()
    virtual_meeting_url = serializers.URLField()
    virtual_meeting_password = serializers.CharField()

    def create(self, validated_data):
        """Not implemented - location data is embedded in Event model"""
        raise NotImplementedError('EventLocationSerializer is read-only')

    def update(self, instance, validated_data):
        """Not implemented - location data is embedded in Event model"""
        raise NotImplementedError('EventLocationSerializer is read-only')


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists and cards"""
    event_type_name = serializers.CharField(
        source='event_type.name', read_only=True)
    category_name = serializers.CharField(
        source='event_type.category.name', read_only=True)

    # Location summary
    city_name = serializers.CharField(source='city.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    # Computed fields
    is_registration_open = serializers.BooleanField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    funding_percentage = serializers.FloatField(read_only=True)

    # Counts
    participants_count = serializers.SerializerMethodField()
    sponsors_count = serializers.SerializerMethodField()

    class Meta:
        """Meta information for the EventListSerializer"""
        model = Event
        fields = [
            'id', 'uuid', 'title', 'slug', 'short_description',
            'event_type', 'event_type_name', 'category_name',
            'status', 'visibility', 'is_featured', 'is_virtual',
            # Location
            'city_name', 'state_name', 'country_name', 'location_name',
            'latitude', 'longitude',
            # Timing
            'start_datetime', 'end_datetime', 'timezone',
            # Media
            'thumbnail_image', 'banner_image',
            # Financial
            'funding_goal', 'current_funding', 'currency', 'funding_percentage',
            # Computed
            'is_registration_open', 'is_full',
            'participants_count', 'sponsors_count',
            # Metadata
            'created_at', 'updated_at'
        ]

    def get_participants_count(self, obj):
        """Get count of registered participants"""
        return obj.participants.filter(status='registered').count()

    def get_sponsors_count(self, obj):
        """Get count of public sponsors"""
        return obj.sponsors.filter(is_public=True).count()


class EventDetailSerializer(serializers.ModelSerializer):
    """Full event details with all related data"""
    event_type = EventTypeSerializer(read_only=True)

    # Location with full details
    location = serializers.SerializerMethodField()

    # Relations
    target_school = SimpleSchoolSerializer(read_only=True)
    target_organization = OrganizationSerializer(read_only=True)

    # Related data (will be added via serializers)
    organizers = serializers.SerializerMethodField()
    sponsors = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    milestones = serializers.SerializerMethodField()
    impact_metrics = serializers.SerializerMethodField()

    # Computed
    is_registration_open = serializers.BooleanField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    funding_percentage = serializers.FloatField(read_only=True)
    full_address = serializers.CharField(read_only=True)

    # Stats
    participants_count = serializers.SerializerMethodField()
    attended_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        """Meta information for the EventDetailSerializer"""
        model = Event
        fields = '__all__'

    def get_location(self, obj):
        """Return structured location data"""
        return EventLocationSerializer(obj).data

    def get_organizers(self, obj):
        """Get event organizers"""
        return EventOrganizerSerializer(
            obj.organizers.all(),
            many=True,
            context=self.context
        ).data

    def get_sponsors(self, obj):
        """Get public sponsors"""
        return EventSponsorSerializer(
            obj.sponsors.filter(is_public=True).order_by('display_order'),
            many=True,
            context=self.context
        ).data

    def get_tickets(self, obj):
        """Get active ticket types"""
        return EventTicketSerializer(
            obj.tickets.filter(status='active').order_by('display_order'),
            many=True,
            context=self.context
        ).data

    def get_photos(self, obj):
        """Get public featured photos"""
        return EventPhotoSerializer(
            obj.photos.filter(is_public=True, is_featured=True).order_by(
                'display_order')[:12],
            many=True,
            context=self.context
        ).data

    def get_updates(self, obj):
        """Get recent public updates"""
        return EventUpdateSerializer(
            obj.updates.filter(is_public=True).order_by(
                '-is_pinned', '-posted_at')[:5],
            many=True,
            context=self.context
        ).data

    def get_milestones(self, obj):
        """Get event milestones"""
        return EventMilestoneSerializer(
            obj.milestones.all().order_by('display_order'),
            many=True,
            context=self.context
        ).data

    def get_impact_metrics(self, obj):
        """Get event impact metrics"""
        return EventImpactSerializer(
            obj.impact_metrics.all().order_by('display_order'),
            many=True,
            context=self.context
        ).data

    def get_participants_count(self, obj):
        """Get count of registered participants"""
        return obj.participants.filter(status__in=['registered', 'confirmed', 'attended']).count()

    def get_attended_count(self, obj):
        """Get count of participants who attended"""
        return obj.participants.filter(status='attended').count()

    def get_average_rating(self, obj):
        """Calculate average overall rating from feedback"""
        avg = obj.feedback.filter(
            is_public=True).aggregate(Avg('overall_rating'))
        return round(avg['overall_rating__avg'], 1) if avg['overall_rating__avg'] else None


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events"""

    class Meta:
        """Meta information for the EventCreateUpdateSerializer"""
        model = Event
        fields = [
            'title', 'slug', 'description', 'short_description',
            'event_type', 'tags',
            # Target
            'target_school', 'target_organization',
            # Location
            'country', 'state', 'city', 'village',
            'address_line_1', 'address_line_2', 'postal_code',
            'latitude', 'longitude', 'location_name',
            'location_instructions', 'google_maps_url',
            # Virtual
            'is_virtual', 'virtual_meeting_url', 'virtual_meeting_password',
            # Schedule
            'start_datetime', 'end_datetime', 'timezone',
            'registration_start', 'registration_deadline', 'max_participants',
            # Media
            'banner_image', 'thumbnail_image', 'video_url',
            # Financial
            'funding_goal', 'currency',
            # Settings
            'status', 'visibility', 'requires_approval', 'is_featured',
            # SEO
            'meta_description', 'og_image',
        ]

    def validate(self, attrs):
        """Custom validation for location data"""
        # Ensure virtual events have meeting URL
        if attrs.get('is_virtual') and not attrs.get('virtual_meeting_url'):
            raise serializers.ValidationError({
                'virtual_meeting_url': 'Virtual events require a meeting URL'
            })

        # Physical events need location
        if not attrs.get('is_virtual'):
            has_coordinates = attrs.get('latitude') and attrs.get('longitude')
            has_address = attrs.get(
                'address_line_1') or attrs.get('location_name')

            if not (has_coordinates or has_address):
                raise serializers.ValidationError(
                    'Physical events need either coordinates (lat/lon) or an address'
                )

        # Date validation
        if attrs.get('start_datetime') and attrs.get('end_datetime'):
            if attrs['start_datetime'] >= attrs['end_datetime']:
                raise serializers.ValidationError({
                    'end_datetime': 'End date must be after start date'
                })

        return attrs

    def create(self, validated_data):
        """Set the creator when creating"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EventSearchSerializer(serializers.Serializer):
    """Serializer for event search with geolocation filters"""
    query = serializers.CharField(required=False, allow_blank=True)
    event_type = serializers.IntegerField(required=False)
    category = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    country = serializers.IntegerField(required=False)
    state = serializers.IntegerField(required=False)
    city = serializers.IntegerField(required=False)

    # Geolocation-based search (find events near me)
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False)
    radius_km = serializers.IntegerField(
        required=False, default=50, min_value=1, max_value=500)

    # Date filters
    start_date_from = serializers.DateTimeField(required=False)
    start_date_to = serializers.DateTimeField(required=False)

    # Other filters
    is_virtual = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)
    has_funding = serializers.BooleanField(required=False)

    # Pagination
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(
        required=False, default=20, min_value=1, max_value=100)

    def create(self, validated_data):
        """Not implemented - search serializer is for filtering only"""
        raise NotImplementedError('EventSearchSerializer is read-only')

    def update(self, instance, validated_data):
        """Not implemented - search serializer is for filtering only"""
        raise NotImplementedError('EventSearchSerializer is read-only')
