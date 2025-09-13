"""
Serializers for Ads Manager API endpoints.
"""

from django.core.exceptions import ValidationError
from rest_framework import serializers

from ads.models import (AdClick, AdImpression, AdManager, AdPlacement, AdSpace,
                        AdType, UserBehavior, UserProfile)


class AdTypeSerializer(serializers.ModelSerializer):
    """Serializer for Ad Types."""

    class Meta:
        model = AdType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class AdSpaceSerializer(serializers.ModelSerializer):
    """Serializer for Ad Spaces."""

    placement_count = serializers.SerializerMethodField()

    class Meta:
        model = AdSpace
        fields = ['id', 'name', 'slug', 'placement_count']
        read_only_fields = ['id', 'placement_count']

    def get_placement_count(self, obj):
        """Get the number of active placements for this ad space."""
        return obj.placements.filter(ad__is_active=True).count()


class AdManagerListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing ads."""

    ad_type_name = serializers.CharField(source='ad_type.name', read_only=True)
    placement_count = serializers.SerializerMethodField()
    is_currently_active = serializers.ReadOnlyField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = AdManager
        fields = [
            'uuid', 'campaign_title', 'description', 'ad_type_name', 'start_datetime',
            'end_datetime', 'target_url', 'is_active', 'is_currently_active',
            'placement_count', 'days_remaining', 'create_datetime', 'poster'
        ]
        read_only_fields = [
            'uuid', 'is_currently_active', 'placement_count',
            'days_remaining', 'create_datetime', 'poster'
        ]

    def get_placement_count(self, obj):
        """Get the number of placements for this ad."""
        return obj.placements.count()

    def get_days_remaining(self, obj):
        """Calculate days remaining until ad expires."""
        if not obj.end_datetime:
            return None

        from datetime import date
        today = date.today()

        if obj.end_datetime < today:
            return 0  # Expired

        return (obj.end_datetime - today).days


class AdManagerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for ad management."""

    ad_type_name = serializers.CharField(source='ad_type.name', read_only=True)
    placements = serializers.SerializerMethodField()
    is_currently_active = serializers.ReadOnlyField()
    impression_count = serializers.SerializerMethodField()
    click_count = serializers.SerializerMethodField()
    click_through_rate = serializers.SerializerMethodField()

    class Meta:
        model = AdManager
        fields = [
            'uuid', 'campaign_title', 'description', 'ad_type', 'ad_type_name', 'tags',
            'start_datetime', 'end_datetime', 'target_url', 'is_active', 'is_currently_active',
            'active_ad_period', 'limited_overdue', 'poster', 'placements',
            'impression_count', 'click_count', 'click_through_rate',
            'update_datetime', 'create_datetime'
        ]
        read_only_fields = [
            'uuid', 'is_currently_active', 'active_ad_period', 'placements',
            'impression_count', 'click_count', 'click_through_rate',
            'update_datetime', 'create_datetime'
        ]

    def get_placements(self, obj):
        """Get placement details for this ad."""
        placements = obj.placements.select_related('ad_space').all()
        return AdPlacementSerializer(placements, many=True).data

    def get_impression_count(self, obj):
        """Get total impressions for this ad."""
        return obj.adimpression_set.count()

    def get_click_count(self, obj):
        """Get total clicks for this ad."""
        return obj.adclick_set.count()

    def get_click_through_rate(self, obj):
        """Calculate click-through rate."""
        impressions = self.get_impression_count(obj)
        clicks = self.get_click_count(obj)

        if impressions == 0:
            return 0.0

        return round((clicks / impressions) * 100, 2)


class AdManagerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating ads."""

    class Meta:
        model = AdManager
        fields = [
            'campaign_title', 'description', 'ad_type', 'tags', 'start_datetime',
            'end_datetime', 'target_url', 'is_active', 'limited_overdue', 'poster'
        ]

    def validate(self, data):
        """Validate ad data."""
        start_date = data.get('start_datetime')
        end_date = data.get('end_datetime')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_datetime': 'End date must be after start date.'
            })

        return data

    def validate_tags(self, value):
        """Validate tags field."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Tags must be a list.')

        # Ensure all tags are strings
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError('All tags must be strings.')

        return value


class AdPlacementSerializer(serializers.ModelSerializer):
    """Serializer for Ad Placements."""

    ad_title = serializers.CharField(
        source='ad.campaign_title', read_only=True)
    ad_space_name = serializers.CharField(
        source='ad_space.name', read_only=True)

    class Meta:
        model = AdPlacement
        fields = [
            'id', 'ad', 'ad_space', 'ad_title', 'ad_space_name',
            'position', 'is_primary'
        ]
        read_only_fields = ['id', 'ad_title', 'ad_space_name']

    def validate(self, data):
        """Validate placement data."""
        ad = data.get('ad')
        ad_space = data.get('ad_space')

        # Check for existing placement
        if ad and ad_space:
            existing = AdPlacement.objects.filter(ad=ad, ad_space=ad_space)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)

            if existing.exists():
                raise serializers.ValidationError(
                    'This ad is already placed in this ad space.'
                )

        return data


class AdImpressionSerializer(serializers.ModelSerializer):
    """Serializer for Ad Impressions."""

    ad_title = serializers.CharField(
        source='ad.campaign_title', read_only=True)

    class Meta:
        model = AdImpression
        fields = [
            'id', 'ad', 'ad_title', 'user_id', 'session_id',
            'timestamp', 'user_agent', 'ip_address'
        ]
        read_only_fields = ['id', 'ad_title', 'timestamp']


class AdClickSerializer(serializers.ModelSerializer):
    """Serializer for Ad Clicks."""

    ad_title = serializers.CharField(
        source='ad.campaign_title', read_only=True)

    class Meta:
        model = AdClick
        fields = [
            'id', 'ad', 'ad_title', 'user_id', 'timestamp', 'referrer'
        ]
        read_only_fields = ['id', 'ad_title', 'timestamp']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profiles (targeting)."""

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'interests', 'last_active']
        read_only_fields = ['id', 'last_active']

    def validate_interests(self, value):
        """Validate interests field."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Interests must be a list.')

        # Ensure all interests are strings
        for interest in value:
            if not isinstance(interest, str):
                raise serializers.ValidationError(
                    'All interests must be strings.')

        return value


class UserBehaviorSerializer(serializers.ModelSerializer):
    """Serializer for User Behavior tracking."""

    class Meta:
        model = UserBehavior
        fields = [
            'id', 'user_id', 'session_id', 'page_slug',
            'category', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class AdAnalyticsSerializer(serializers.Serializer):
    """Serializer for ad analytics data."""

    ad_uuid = serializers.UUIDField()
    campaign_title = serializers.CharField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    click_through_rate = serializers.FloatField()
    unique_users = serializers.IntegerField()
    avg_daily_impressions = serializers.FloatField()
    date_range = serializers.CharField()


class AdSpaceAnalyticsSerializer(serializers.Serializer):
    """Serializer for ad space analytics."""

    space_name = serializers.CharField()
    total_ads = serializers.IntegerField()
    active_ads = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    average_ctr = serializers.FloatField()
