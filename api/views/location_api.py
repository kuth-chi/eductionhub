import logging
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers.schools.locations import (CitySerializer,
                                               CitySimpleSerializer,
                                               CountrySerializer,
                                               CountrySimpleSerializer,
                                               StateSerializer,
                                               StateSimpleSerializer,
                                               VillageSerializer,
                                               VillageSimpleSerializer)
from geo.models import City, Country, State, Village

logger = logging.getLogger(__name__)


class CountryViewSet(viewsets.ModelViewSet):
    """ViewSet for Country model"""

    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]
    lookup_field = "uuid"

    @action(detail=False, methods=["get"])
    def simple(self, request):
        """Get simplified country list for dropdowns"""
        countries = self.get_queryset()
        serializer = CountrySimpleSerializer(countries, many=True)
        return Response(serializer.data)


class StateViewSet(viewsets.ModelViewSet):
    """ViewSet for State model"""

    queryset = State.objects.filter(is_active=True).select_related("country")
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country", "is_active"]
    search_fields = ["name", "code", "country__name"]
    ordering_fields = ["name", "code", "country__name"]
    ordering = ["country__name", "name"]
    lookup_field = "uuid"

    def get_queryset(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return State.objects.select_related("country")
        return State.objects.filter(is_active=True).select_related("country")

    @action(detail=False, methods=["get"])
    def by_country(self, request):
        """Get states by country ID"""
        country_id = request.query_params.get("country_id")
        if country_id:
            states = self.get_queryset().filter(country_id=country_id)
            serializer = StateSimpleSerializer(states, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "country_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def simple(self, request):
        """Get simplified state list for dropdowns"""
        states = self.get_queryset()
        serializer = StateSimpleSerializer(states, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet):
    """ViewSet for City model"""

    queryset = City.objects.filter(is_active=True).select_related(
        "state", "state__country"
    )
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state", "state__country", "is_capital", "is_active"]
    search_fields = ["name", "code", "state__name", "state__country__name"]
    ordering_fields = ["name", "code", "state__name"]
    ordering = ["state__country__name", "state__name", "name"]
    lookup_field = "uuid"

    @action(detail=False, methods=["get"])
    def by_state(self, request):
        """Get cities by state ID"""
        state_id = request.query_params.get("state_id")
        if state_id:
            cities = self.get_queryset().filter(state_id=state_id)
            serializer = CitySimpleSerializer(cities, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "state_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def by_country(self, request):
        """Get cities by country ID"""
        country_id = request.query_params.get("country_id")
        if country_id:
            cities = self.get_queryset().filter(state__country_id=country_id)
            serializer = CitySimpleSerializer(cities, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "country_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def simple(self, request):
        """Get simplified city list for dropdowns"""
        logger.info("Request for simplified city list from user: %s", request.user)
        cities = self.get_queryset()
        serializer = CitySimpleSerializer(cities, many=True)
        return Response(serializer.data)


class VillageViewSet(viewsets.ModelViewSet):
    """ViewSet for Village model with enhanced multi-level filtering"""

    queryset = Village.objects.filter(is_active=True).select_related(
        "city", "city__state", "city__state__country"
    )
    serializer_class = VillageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    # Simplified - we'll handle geo filtering manually
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "city__name", "city__state__name"]
    ordering_fields = ["name", "code", "city__name"]
    ordering = ["city__state__country__name",
                "city__state__name", "city__name", "name"]
    lookup_field = "uuid"

    def get_queryset(self):
        """Override to add custom multi-level geographic filtering"""
        if self.action in ["update", "partial_update", "destroy"]:
            # For update/delete operations, include inactive villages
            base_queryset = Village.objects.select_related(
                "city", "city__state", "city__state__country"
            )
        else:
            # For list/retrieve operations, only show active villages
            base_queryset = Village.objects.filter(is_active=True).select_related(
                "city", "city__state", "city__state__country"
            )

        # Apply custom geographic filtering with OR logic
        geo_filter = self._build_geographic_filter()
        if geo_filter:
            base_queryset = base_queryset.filter(geo_filter)

        logger.info(
            "VillageViewSet get_queryset for %s: %d villages",
            self.action,
            base_queryset.count()
        )
        return base_queryset

    def _build_geographic_filter(self):
        """Build OR-based geographic filter from query parameters"""
        request = self.request
        if not request:
            return None

        # Get multiple IDs for each geographic level
        city_ids = self._get_param_list('city')
        state_ids = self._get_param_list('city__state')
        country_ids = self._get_param_list('city__state__country')

        # Build OR conditions for each level
        conditions = []

        # Add city conditions
        if city_ids:
            city_conditions = Q(city_id__in=city_ids)
            conditions.append(city_conditions)
            logger.info("Adding city filter: city_id__in=%s", city_ids)

        # Add state conditions
        if state_ids:
            state_conditions = Q(city__state_id__in=state_ids)
            conditions.append(state_conditions)
            logger.info("Adding state filter: city__state_id__in=%s", state_ids)

        # Add country conditions
        if country_ids:
            country_conditions = Q(city__state__country_id__in=country_ids)
            conditions.append(country_conditions)
            logger.info("Adding country filter: city__state__country_id__in=%s", country_ids)

        # Combine all conditions with OR logic
        if conditions:
            final_filter = conditions[0]
            for condition in conditions[1:]:
                final_filter |= condition  # OR logic
            logger.info("Final geographic filter: %s", final_filter)
            return final_filter

        return None

    def _get_param_list(self, param_name):
        """Extract multiple values for a parameter from query string"""
        if not self.request:
            return []

        values = self.request.query_params.getlist(param_name)
        # Convert to integers and filter out invalid values
        int_values = []
        for value in values:
            try:
                int_values.append(int(value))
            except (ValueError, TypeError):
                logger.warning("Invalid %s value: %s", param_name, value)
        return int_values


    @action(detail=False, methods=["get"])
    def by_city(self, request):
        """Get villages by city ID"""
        city_id = request.query_params.get("city_id")
        if city_id:
            villages = self.get_queryset().filter(city_id=city_id)
            serializer = VillageSimpleSerializer(villages, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "city_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def by_state(self, request):
        """Get villages by state ID"""
        state_id = request.query_params.get("state_id")
        if state_id:
            villages = self.get_queryset().filter(city__state_id=state_id)
            serializer = VillageSimpleSerializer(villages, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "state_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def by_country(self, request):
        """Get villages by country ID"""
        country_id = request.query_params.get("country_id")
        if country_id:
            villages = self.get_queryset().filter(city__state__country_id=country_id)
            serializer = VillageSimpleSerializer(villages, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "country_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def simple(self, request):
        """Get simplified village list for dropdowns"""
        logger.info("Request for simplified village list from user: %s", request.user)
        villages = self.get_queryset()
        serializer = VillageSimpleSerializer(villages, many=True)
        return Response(serializer.data)
