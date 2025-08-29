
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from api.serializers.schools.college_serializers import CollegeSerializer
from api.serializers.schools.locations import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    VillageSerializer
)
from api.serializers.schools.test import SimpleSchoolSerializer
from schools.models.school import SchoolBranch, School
from geo.models import Country, State, City, Village


class SchoolBranchSerializer(serializers.ModelSerializer):
    """Serializer for SchoolBranch model."""
    colleges = CollegeSerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    village = VillageSerializer(read_only=True)
    school = SimpleSchoolSerializer(read_only=True)
    school_id = serializers.CharField(
        write_only=True, required=True, source='school')

    # Write-only fields for geographic relationships
    country_id = serializers.IntegerField(
        write_only=True, required=False, source='country')
    state_id = serializers.IntegerField(
        write_only=True, required=False, source='state')
    city_id = serializers.IntegerField(
        write_only=True, required=False, source='city')
    village_id = serializers.IntegerField(
        write_only=True, required=False, source='village')

    class Meta:
        model = SchoolBranch
        fields = "__all__"
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    def validate_school_id(self, value):
        """Convert school UUID to school instance."""
        if value:
            try:
                # Try to get school by UUID first
                school = School.objects.get(uuid=value)
                return school
            except ObjectDoesNotExist:
                try:
                    # Fallback to primary key if it's a number
                    school = School.objects.get(pk=value)
                    return school
                except (ObjectDoesNotExist, ValueError) as exc:
                    raise serializers.ValidationError(
                        f"School with identifier '{value}' does not exist.") from exc
        raise serializers.ValidationError(
            "School is required for all branches.")

    def validate_country_id(self, value):
        """Validate country ID exists."""
        if value:
            try:
                return Country.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Country with ID '{value}' does not exist.")
        return value

    def validate_state_id(self, value):
        """Validate state ID exists."""
        if value:
            try:
                return State.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"State with ID '{value}' does not exist.")
        return value

    def validate_city_id(self, value):
        """Validate city ID exists."""
        if value:
            try:
                return City.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"City with ID '{value}' does not exist.")
        return value

    def validate_village_id(self, value):
        """Validate village ID exists."""
        if value:
            try:
                return Village.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Village with ID '{value}' does not exist.")
        return value

    def create(self, validated_data):
        """Override create to handle all ID to instance conversions."""
        # Handle school
        school_value = validated_data.pop('school', None)
        if school_value:
            validated_data['school'] = school_value

        # Handle geographic fields
        country_value = validated_data.pop('country', None)
        if country_value:
            validated_data['country'] = country_value

        state_value = validated_data.pop('state', None)
        if state_value:
            validated_data['state'] = state_value

        city_value = validated_data.pop('city', None)
        if city_value:
            validated_data['city'] = city_value

        village_value = validated_data.pop('village', None)
        if village_value:
            validated_data['village'] = village_value

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override update to handle all ID to instance conversions."""
        # Handle school
        school_value = validated_data.pop('school', None)
        if school_value:
            validated_data['school'] = school_value

        # Handle geographic fields
        country_value = validated_data.pop('country', None)
        if country_value:
            validated_data['country'] = country_value

        state_value = validated_data.pop('state', None)
        if state_value:
            validated_data['state'] = state_value

        city_value = validated_data.pop('city', None)
        if city_value:
            validated_data['city'] = city_value

        village_value = validated_data.pop('village', None)
        if village_value:
            validated_data['village'] = village_value

        return super().update(instance, validated_data)
