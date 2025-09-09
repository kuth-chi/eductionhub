
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from api.serializers.schools.college_serializers import CollegeSerializer
from api.serializers.schools.locations import (CitySerializer,
                                               CountrySerializer,
                                               StateSerializer,
                                               VillageSerializer)
from api.serializers.schools.test import SimpleSchoolSerializer
from geo.models import City, Country, State, Village
from schools.models.school import School, SchoolBranch


class SchoolBranchSerializer(serializers.ModelSerializer):
    """Serializer for SchoolBranch model."""
    colleges = CollegeSerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    village = VillageSerializer(read_only=True)
    school = SimpleSchoolSerializer(read_only=True)
    school_id = serializers.CharField(write_only=True, required=True, source='school',
                                      help_text="UUID or ID of the school this branch belongs to")

    # Write-only fields for geographic relationships
    country_id = serializers.IntegerField(
        write_only=True, required=False, source='country',
        help_text="ID of the country where this branch is located")
    state_id = serializers.IntegerField(
        write_only=True, required=False, source='state',
        help_text="ID of the state where this branch is located")
    city_id = serializers.IntegerField(
        write_only=True, required=False, source='city',
        help_text="ID of the city where this branch is located")
    village_id = serializers.IntegerField(
        write_only=True, required=False, source='village',
        help_text="ID of the village where this branch is located")

    class Meta:
        model = SchoolBranch
        fields = "__all__"
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'slug']

    def validate_school_id(self, value):
        """Convert school UUID to school instance."""
        if not value:
            raise serializers.ValidationError(
                "School is required for all branches.")

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
                    f"School with identifier '{value}' does not exist. "
                    f"Please provide a valid school UUID or ID.") from exc

    def validate_name(self, value):
        """Validate branch name is unique within the school"""
        if not value or not value.strip():
            raise serializers.ValidationError("Branch name is required.")

        # If we're creating a new branch, check for name uniqueness within the school
        if not self.instance:  # Creating new branch
            school_value = self.initial_data.get('school_id')
            if school_value:
                try:
                    school = School.objects.get(uuid=school_value)
                    if SchoolBranch.objects.filter(school=school, name=value.strip()).exists():
                        raise serializers.ValidationError(
                            f"A branch with the name '{value.strip()}' already exists for this school.")
                except School.DoesNotExist:
                    pass  # School validation will handle this
        return value.strip()

    def validate_address(self, value):
        """Validate address is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Address is required for all branches.")
        return value.strip()

    def validate_country_id(self, value):
        """Validate country ID exists."""
        if value:
            try:
                return Country.objects.get(pk=value)
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError(
                    f"Country with ID '{value}' does not exist.") from exc
        return value

    def validate_state_id(self, value):
        """Validate state ID exists."""
        if value:
            try:
                return State.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"State with ID '{value}' does not exist.")
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

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate headquarters logic
        is_headquarters = attrs.get('is_headquarters', False)
        school = attrs.get('school')

        if is_headquarters and school:
            # Check if there's already a headquarters for this school
            existing_hq = SchoolBranch.objects.filter(
                school=school, is_headquarters=True
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing_hq.exists():
                raise serializers.ValidationError({
                    'is_headquarters': 'This school already has a headquarters branch. '
                    'You can only have one headquarters per school.'
                })

        return super().validate(attrs)

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
