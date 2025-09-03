"""
ViewSets for Ads Manager API endpoints.
"""

from datetime import date, timedelta
import logging
from django.db.models import Avg, Count, F, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters_rf
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from ads.models import (AdClick, AdImpression, AdManager, AdPlacement, AdSpace,
                        AdType, UserBehavior, UserProfile)
from api.serializers.ads_manager import (AdAnalyticsSerializer,
                                         AdClickSerializer,
                                         AdImpressionSerializer,
                                         AdManagerCreateUpdateSerializer,
                                         AdManagerDetailSerializer,
                                         AdManagerListSerializer,
                                         AdPlacementSerializer,
                                         AdSpaceAnalyticsSerializer,
                                         AdSpaceSerializer, AdTypeSerializer,
                                         UserBehaviorSerializer,
                                         UserProfileSerializer)

logger = logging.getLogger(__name__)


class AdTypeFilter(filters_rf.FilterSet):
    """Filter for Ad Types."""

    name = filters_rf.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AdType
        fields = ['name']


class AdSpaceFilter(filters_rf.FilterSet):
    """Filter for Ad Spaces."""

    name = filters_rf.CharFilter(lookup_expr='icontains')
    slug = filters_rf.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AdSpace
        fields = ['name', 'slug']


class AdManagerFilter(filters_rf.FilterSet):
    """Filter for Ad Manager."""

    campaign_title = filters_rf.CharFilter(lookup_expr='icontains')
    ad_type = filters_rf.ModelChoiceFilter(queryset=AdType.objects.all())
    is_active = filters_rf.BooleanFilter()
    is_currently_active = filters_rf.BooleanFilter(
        method='filter_currently_active')
    start_date_after = filters_rf.DateFilter(
        field_name='start_datetime', lookup_expr='gte')
    start_date_before = filters_rf.DateFilter(
        field_name='start_datetime', lookup_expr='lte')
    end_date_after = filters_rf.DateFilter(
        field_name='end_datetime', lookup_expr='gte')
    end_date_before = filters_rf.DateFilter(
        field_name='end_datetime', lookup_expr='lte')
    tags = filters_rf.CharFilter(method='filter_tags')

    class Meta:
        model = AdManager
        fields = [
            'campaign_title', 'ad_type', 'is_active', 'is_currently_active',
            'start_date_after', 'start_date_before', 'end_date_after', 'end_date_before',
            'tags'
        ]

    def filter_currently_active(self, queryset, name, value):
        """Filter by currently active ads."""
        today = date.today()

        if value:
            return queryset.filter(
                is_active=True
            ).filter(
                Q(start_datetime__isnull=True) | Q(start_datetime__lte=today)
            ).filter(
                Q(end_datetime__isnull=True) | Q(end_datetime__gte=today)
            )
        else:
            return queryset.filter(
                Q(is_active=False) |
                Q(start_datetime__gt=today) |
                Q(end_datetime__lt=today)
            )

    def filter_tags(self, queryset, name, value):
        """Filter by tags (contains search)."""
        return queryset.filter(tags__icontains=value)


class AdTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Types."""

    queryset = AdType.objects.all()
    serializer_class = AdTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdTypeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']


class AdSpaceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Spaces."""

    queryset = AdSpace.objects.all()
    serializer_class = AdSpaceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdSpaceFilter
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'id']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific ad space."""
        ad_space = self.get_object()

        # Get placements for this space
        placements = AdPlacement.objects.filter(ad_space=ad_space)

        # Calculate statistics
        total_ads = placements.count()
        active_ads = placements.filter(ad__is_active=True).count()

        # Get impressions and clicks
        ad_ids = placements.values_list('ad_id', flat=True)
        total_impressions = AdImpression.objects.filter(
            ad_id__in=ad_ids).count()
        total_clicks = AdClick.objects.filter(ad_id__in=ad_ids).count()

        # Calculate average CTR
        average_ctr = 0.0
        if total_impressions > 0:
            average_ctr = round((total_clicks / total_impressions) * 100, 2)

        analytics_data = {
            'space_name': ad_space.name,
            'total_ads': total_ads,
            'active_ads': active_ads,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'average_ctr': average_ctr,
        }

        serializer = AdSpaceAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class AdManagerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Campaigns."""

    queryset = AdManager.objects.select_related(
        'ad_type').prefetch_related('placements__ad_space')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AdManagerFilter
    search_fields = ['campaign_title', 'tags']
    ordering_fields = ['campaign_title', 'start_datetime',
                       'end_datetime', 'create_datetime']
    ordering = ['-create_datetime']

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'list':
            return AdManagerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AdManagerCreateUpdateSerializer
        else:
            return AdManagerDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = super().get_queryset()

        # Add any user-specific filtering here if needed
        # For now, return all ads for authenticated users
        return queryset

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an ad campaign."""
        ad = self.get_object()
        ad.is_active = True
        ad.save()

        serializer = self.get_serializer(ad)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an ad campaign."""
        ad = self.get_object()
        ad.is_active = False
        ad.save()

        serializer = self.get_serializer(ad)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific ad campaign."""
        ad = self.get_object()

        # Get date range for analytics
        days = int(request.query_params.get('days', 30))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Calculate statistics
        impressions = AdImpression.objects.filter(
            ad=ad,
            timestamp__date__range=[start_date, end_date]
        )
        clicks = AdClick.objects.filter(
            ad=ad,
            timestamp__date__range=[start_date, end_date]
        )

        total_impressions = impressions.count()
        total_clicks = clicks.count()
        unique_users = impressions.values('user_id').distinct().count()

        # Calculate CTR
        click_through_rate = 0.0
        if total_impressions > 0:
            click_through_rate = round(
                (total_clicks / total_impressions) * 100, 2)

        # Calculate average daily impressions
        avg_daily_impressions = round(
            total_impressions / days, 2) if days > 0 else 0

        analytics_data = {
            'ad_uuid': ad.uuid,
            'campaign_title': ad.campaign_title,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'click_through_rate': click_through_rate,
            'unique_users': unique_users,
            'avg_daily_impressions': avg_daily_impressions,
            'date_range': f'{start_date} to {end_date}',
        }

        serializer = AdAnalyticsSerializer(analytics_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for all ads."""
        today = date.today()

        # Total ads
        total_ads = self.get_queryset().count()

        # Active ads
        active_ads = self.get_queryset().filter(
            is_active=True
        ).filter(
            Q(start_datetime__isnull=True) | Q(start_datetime__lte=today)
        ).filter(
            Q(end_datetime__isnull=True) | Q(end_datetime__gte=today)
        ).count()

        # Expiring soon (next 7 days)
        expiring_soon = self.get_queryset().filter(
            is_active=True,
            end_datetime__range=[today, today + timedelta(days=7)]
        ).count()

        # Total impressions (last 30 days)
        last_30_days = today - timedelta(days=30)
        total_impressions = AdImpression.objects.filter(
            timestamp__date__gte=last_30_days
        ).count()

        # Total clicks (last 30 days)
        total_clicks = AdClick.objects.filter(
            timestamp__date__gte=last_30_days
        ).count()

        # Average CTR
        avg_ctr = 0.0
        if total_impressions > 0:
            avg_ctr = round((total_clicks / total_impressions) * 100, 2)

        stats = {
            'total_ads': total_ads,
            'active_ads': active_ads,
            'expiring_soon': expiring_soon,
            'total_impressions_30d': total_impressions,
            'total_clicks_30d': total_clicks,
            'average_ctr_30d': avg_ctr,
        }

        return Response(stats)


class AdPlacementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Placements."""

    queryset = AdPlacement.objects.select_related('ad', 'ad_space').all()
    serializer_class = AdPlacementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ad', 'ad_space', 'is_primary']
    ordering_fields = ['position', 'id']
    ordering = ['ad_space', 'position']

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder placements within an ad space."""
        ad_space_id = request.data.get('ad_space_id')
        placement_ids = request.data.get('placement_ids', [])

        if not ad_space_id or not placement_ids:
            return Response(
                {'error': 'ad_space_id and placement_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Update positions
            for index, placement_id in enumerate(placement_ids, 1):
                AdPlacement.objects.filter(
                    id=placement_id,
                    ad_space_id=ad_space_id
                ).update(position=index)

            return Response({'success': True})

        except Exception as e:
            logger.exception(
                "Failed to reorder placements due to an unexpected error. %s", str(e))

            # 2. RETURN A GENERIC RESPONSE: The user only gets a vague, safe message.
            return Response(
                {'error': 'An unexpected error occurred while processing your request. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdImpressionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Impressions."""

    queryset = AdImpression.objects.select_related('ad').all()
    serializer_class = AdImpressionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ad', 'user_id']
    ordering_fields = ['timestamp', 'id']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Limit queryset to recent impressions for performance."""
        # Only show impressions from the last 90 days by default
        days = int(self.request.query_params.get('days', 90))
        cutoff_date = date.today() - timedelta(days=days)

        return super().get_queryset().filter(
            timestamp__date__gte=cutoff_date
        )


class AdClickViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Ad Clicks."""

    queryset = AdClick.objects.select_related('ad').all()
    serializer_class = AdClickSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ad', 'user_id']
    ordering_fields = ['timestamp', 'id']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Limit queryset to recent clicks for performance."""
        # Only show clicks from the last 90 days by default
        days = int(self.request.query_params.get('days', 90))
        cutoff_date = date.today() - timedelta(days=days)

        return super().get_queryset().filter(
            timestamp__date__gte=cutoff_date
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing User Profiles (targeting)."""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id']
    search_fields = ['user_id', 'interests']
    ordering_fields = ['last_active', 'user_id']
    ordering = ['-last_active']


class UserBehaviorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing User Behavior."""

    queryset = UserBehavior.objects.all()
    serializer_class = UserBehaviorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id', 'session_id', 'category']
    search_fields = ['user_id', 'page_slug', 'category']
    ordering_fields = ['timestamp', 'id']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Limit queryset to recent behavior for performance."""
        # Only show behavior from the last 30 days by default
        days = int(self.request.query_params.get('days', 30))
        cutoff_date = date.today() - timedelta(days=days)

        return super().get_queryset().filter(
            timestamp__date__gte=cutoff_date
        )
