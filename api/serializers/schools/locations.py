from rest_framework import serializers
from geo.models import Country, State, City, Village


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model"""

    class Meta:
        model = Country
        fields = [
            "id",
            "uuid",
            "name",
            "local_name",
            "code",
            "phone_code",
            "flag_emoji",
            "created_date",
            "updated_date",
            "is_active",
            "is_deleted",
        ]


class StateSerializer(serializers.ModelSerializer):
    """Serializer for State model"""

    country = CountrySerializer(read_only=True)
    country_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = State
        fields = [
            "id",
            "uuid",
            "name",
            "local_name",
            "code",
            "country",
            "country_id",
            "created_date",
            "updated_date",
            "is_active",
            "is_deleted",
        ]


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""

    state = StateSerializer(read_only=True)
    state_id = serializers.IntegerField(write_only=True)
    country = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            "id",
            "uuid",
            "name",
            "local_name",
            "code",
            "state",
            "state_id",
            "is_capital",
            "country",
            "created_date",
            "updated_date",
            "is_active",
            "is_deleted",
        ]

    def get_country(self, obj):
        return CountrySerializer(obj.country).data


class VillageSerializer(serializers.ModelSerializer):
    """Serializer for Village model"""

    city = CitySerializer(read_only=True)
    city_id = serializers.IntegerField(write_only=True)
    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = [
            "id",
            "uuid",
            "name",
            "local_name",
            "code",
            "city",
            "city_id",
            "state",
            "country",
            "created_date",
            "updated_date",
            "is_active",
            "is_deleted",
        ]

    def get_state(self, obj):
        return StateSerializer(obj.state).data

    def get_country(self, obj):
        return CountrySerializer(obj.country).data


# Nested serializers for dropdowns and simplified views
class CountrySimpleSerializer(serializers.ModelSerializer):
    """Simplified Country serializer for dropdowns"""

    class Meta:
        model = Country
        fields = ["id", "name", "local_name", "code", "flag_emoji"]


class StateSimpleSerializer(serializers.ModelSerializer):
    """Simplified State serializer for dropdowns"""

    country = CountrySimpleSerializer(read_only=True)

    class Meta:
        model = State
        fields = ["id", "name", "local_name", "code", "country"]


class CitySimpleSerializer(serializers.ModelSerializer):
    """Simplified City serializer for dropdowns"""

    state = StateSimpleSerializer(read_only=True)

    class Meta:
        model = City
        fields = ["id", "name", "local_name", "code", "state", "is_capital"]


class VillageSimpleSerializer(serializers.ModelSerializer):
    """Simplified Village serializer for dropdowns"""

    city = CitySimpleSerializer(read_only=True)

    class Meta:
        model = Village
        fields = ["id", "name", "local_name", "code", "city"]
