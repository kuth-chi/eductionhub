import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from geo.models import Country, State, City, Village
from api.serializers.schools.locations import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    VillageSerializer,
    CountrySimpleSerializer,
    StateSimpleSerializer,
    CitySimpleSerializer,
    VillageSimpleSerializer,
)

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
        cities = self.get_queryset()
        serializer = CitySimpleSerializer(cities, many=True)
        return Response(serializer.data)


class VillageViewSet(viewsets.ModelViewSet):
    """ViewSet for Village model"""

    queryset = Village.objects.filter(is_active=True).select_related(
        "city", "city__state", "city__state__country"
    )
    serializer_class = VillageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["city", "city__state", "city__state__country", "is_active"]
    search_fields = ["name", "code", "city__name", "city__state__name"]
    ordering_fields = ["name", "code", "city__name"]
    ordering = ["city__state__country__name", "city__state__name", "city__name", "name"]
    lookup_field = "uuid"

    def get_queryset(self):
        """Override to allow updates on inactive villages"""
        if self.action in ["update", "partial_update", "destroy"]:
            # For update/delete operations, include inactive villages
            queryset = Village.objects.select_related(
                "city", "city__state", "city__state__country"
            )
            logger.info(
                f"VillageViewSet get_queryset for {self.action}: {queryset.count()} villages (including inactive)"
            )
            return queryset
        # For list/retrieve operations, only show active villages
        queryset = Village.objects.filter(is_active=True).select_related(
            "city", "city__state", "city__state__country"
        )
        logger.info(
            f"VillageViewSet get_queryset for {self.action}: {queryset.count()} active villages"
        )
        return queryset

    def update(self, request, *args, **kwargs):
        """Override update method to add debugging"""
        logger.info(f"VillageViewSet update called with pk: {kwargs.get('pk')}")
        logger.info(f"Request user: {request.user}")
        logger.info(f"Request method: {request.method}")
        return super().update(request, *args, **kwargs)

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
        villages = self.get_queryset()
        serializer = VillageSimpleSerializer(villages, many=True)
        return Response(serializer.data)
