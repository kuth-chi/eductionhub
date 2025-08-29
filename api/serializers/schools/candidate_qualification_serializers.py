# api/serializers/schools/candidate_qualification_serializers.py
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from schools.models.levels import (CandidateQualification, EducationDegree,
                                   Major)


class EducationDegreeForQualificationSerializer(serializers.ModelSerializer):
    """Simplified serializer for EducationDegree when used in candidate qualifications"""

    name = serializers.SerializerMethodField()

    class Meta:
        model = EducationDegree
        fields = ("id", "uuid", "name", "duration_years",
                  "credit_hours", "is_active")

    def get_name(self, obj):
        return getattr(obj, "name", None) or getattr(obj, "degree_name", None)


class MajorForQualificationSerializer(serializers.ModelSerializer):
    """Simplified serializer for Major when used in candidate qualifications"""

    class Meta:
        model = Major
        fields = ("id", "uuid", "name", "code", "career_paths",
                  "industry_focus", "is_active")


class CandidateQualificationSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for CandidateQualification model.

    Features:
    - Read: Expands related fields (required_degree, major) with nested objects
    - Write: Accepts UUIDs for foreign key relationships
    - Validation: Validates GPA, English score ranges and age format
    - Error handling: Provides clear error messages for invalid data
    """

    # Read-only nested serializers for expanded data
    required_degree = EducationDegreeForQualificationSerializer(read_only=True)
    major = MajorForQualificationSerializer(read_only=True)

    # Write-only UUID fields for creating/updating relationships
    required_degree_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="UUID of the required education degree"
    )
    major_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="UUID of the associated major"
    )

    # Enhanced fields with validation
    min_gpa = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0.00'),
        max_value=Decimal('4.00'),
        help_text="Minimum GPA requirement (0.00 - 4.00)"
    )

    min_english_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
        help_text="Minimum English proficiency score (0.00 - 100.00)"
    )

    age_range = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Age range requirement (e.g., '18-25', '26-30')"
    )

    required_subjects = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="List of required subjects in JSON format"
    )

    class Meta:
        model = CandidateQualification
        fields = [
            "id",
            "uuid",
            "required_subjects",
            "required_degree",
            "required_degree_uuid",
            "major",
            "major_uuid",
            "min_gpa",
            "min_english_score",
            "age_range",
            "qualifications",
            "is_active",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ("id", "uuid", "created_at", "updated_at")

    def validate_age_range(self, value):
        """
        Validate age range format.
        Expected formats: "18-25", "26-30", "18+", "25 and above", etc.
        """
        if not value:
            return value

        # Basic validation for common age range patterns
        import re

        # Pattern for "18-25", "26-30", etc.
        range_pattern = re.compile(r'^\d{1,2}-\d{1,2}$')
        # Pattern for "18+", "25+"
        plus_pattern = re.compile(r'^\d{1,2}\+$')
        # Pattern for "18 and above", "25 and above"
        above_pattern = re.compile(r'^\d{1,2}\s+and\s+above$', re.IGNORECASE)

        if not (range_pattern.match(value) or plus_pattern.match(value) or above_pattern.match(value)):
            # Allow flexible format but provide guidance
            if not any(char.isdigit() for char in value):
                raise serializers.ValidationError(
                    "Age range must contain numeric values. "
                    "Examples: '18-25', '26+', '18 and above'"
                )

        return value

    def validate_required_subjects(self, value):
        """
        Validate required_subjects JSON structure.
        Expected format: ["Math", "Physics", "Chemistry"] or 
        [{"name": "Math", "level": "Advanced"}, ...]
        """
        if value is None:
            return value

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Required subjects must be a list of subjects."
            )

        # Validate each subject entry
        for subject in value:
            if isinstance(subject, str):
                # Simple string format is allowed
                continue
            elif isinstance(subject, dict):
                # Object format should have at least 'name'
                if 'name' not in subject:
                    raise serializers.ValidationError(
                        "Each subject object must have a 'name' field."
                    )
            else:
                raise serializers.ValidationError(
                    "Each subject must be either a string or an object with 'name' field."
                )

        return value

    def validate(self, attrs):
        """
        Cross-field validation for the qualification data.
        """
        min_gpa = attrs.get('min_gpa')
        min_english_score = attrs.get('min_english_score')
        required_degree_uuid = attrs.get('required_degree_uuid')
        major_uuid = attrs.get('major_uuid')

        # Validate GPA and English score relationship
        if min_gpa and min_english_score:
            if min_gpa > Decimal('4.00') or min_english_score > Decimal('100.00'):
                raise serializers.ValidationError(
                    "Invalid score values. GPA must be ≤ 4.00 and English score ≤ 100.00"
                )

        # Ensure at least one qualification criterion is specified
        criteria_fields = [
            'min_gpa', 'min_english_score', 'age_range',
            'required_subjects', 'qualifications'
        ]
        has_criteria = any(attrs.get(field) for field in criteria_fields)
        has_relationships = required_degree_uuid or major_uuid

        if not (has_criteria or has_relationships):
            raise serializers.ValidationError(
                "At least one qualification criterion or relationship must be specified."
            )

        return attrs

    def create(self, validated_data):
        """
        Create a new CandidateQualification instance with proper relationship handling.
        """
        required_degree_uuid = validated_data.pop('required_degree_uuid', None)
        major_uuid = validated_data.pop('major_uuid', None)

        # Handle required_degree relationship
        if required_degree_uuid:
            try:
                required_degree = EducationDegree.objects.get(
                    uuid=required_degree_uuid,
                    is_active=True,
                    is_deleted=False
                )
                validated_data['required_degree'] = required_degree
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "required_degree_uuid": "Education degree with this UUID does not exist or is not active."
                }) from exc

        # Handle major relationship
        if major_uuid:
            try:
                major = Major.objects.get(
                    uuid=major_uuid,
                    is_active=True,
                    is_deleted=False
                )
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "major_uuid": "Major with this UUID does not exist or is not active."
                }) from exc

        return CandidateQualification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing CandidateQualification instance with proper relationship handling.
        """
        required_degree_uuid = validated_data.pop('required_degree_uuid', None)
        major_uuid = validated_data.pop('major_uuid', None)

        # Handle required_degree relationship
        if required_degree_uuid:
            try:
                required_degree = EducationDegree.objects.get(
                    uuid=required_degree_uuid,
                    is_active=True,
                    is_deleted=False
                )
                validated_data['required_degree'] = required_degree
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "required_degree_uuid": "Education degree with this UUID does not exist or is not active."
                }) from exc

        # Handle major relationship
        if major_uuid:
            try:
                major = Major.objects.get(
                    uuid=major_uuid,
                    is_active=True,
                    is_deleted=False
                )
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "major_uuid": "Major with this UUID does not exist or is not active."
                }) from exc

        # Update instance with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Customize the output representation to include additional helpful information.
        """
        representation = super().to_representation(instance)

        # Add UUID references for easier frontend handling
        if instance.required_degree:
            representation['required_degree_uuid'] = str(
                instance.required_degree.uuid)
        if instance.major:
            representation['major_uuid'] = str(instance.major.uuid)

        # Add computed fields for better frontend experience
        representation['has_gpa_requirement'] = bool(instance.min_gpa)
        representation['has_english_requirement'] = bool(
            instance.min_english_score)
        representation['has_age_requirement'] = bool(instance.age_range)
        representation['has_subject_requirements'] = bool(
            instance.required_subjects)

        # Format subjects for display if they exist
        if instance.required_subjects:
            subjects_display = []
            for subject in instance.required_subjects:
                if isinstance(subject, str):
                    subjects_display.append(subject)
                elif isinstance(subject, dict) and 'name' in subject:
                    level = subject.get('level', '')
                    subjects_display.append(
                        f"{subject['name']} ({level})" if level else subject['name'])
            representation['subjects_display'] = subjects_display

        return representation


class CreateCandidateQualificationSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for creating candidate qualifications with required fields.
    """

    required_degree_uuid = serializers.UUIDField(
        required=False, allow_null=True)
    major_uuid = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = CandidateQualification
        fields = [
            "required_subjects",
            "required_degree_uuid",
            "major_uuid",
            "min_gpa",
            "min_english_score",
            "age_range",
            "qualifications",
            "is_active"
        ]

    def validate(self, attrs):
        """Ensure at least one criterion is provided"""
        criteria_fields = [
            'min_gpa', 'min_english_score', 'age_range',
            'required_subjects', 'qualifications'
        ]
        has_criteria = any(attrs.get(field) for field in criteria_fields)
        has_relationships = attrs.get(
            'required_degree_uuid') or attrs.get('major_uuid')

        if not (has_criteria or has_relationships):
            raise serializers.ValidationError(
                "At least one qualification criterion or relationship must be specified."
            )

        return attrs

    def create(self, validated_data):
        required_degree_uuid = validated_data.pop('required_degree_uuid', None)
        major_uuid = validated_data.pop('major_uuid', None)

        if required_degree_uuid:
            try:
                required_degree = EducationDegree.objects.get(
                    uuid=required_degree_uuid)
                validated_data['required_degree'] = required_degree
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "required_degree_uuid": "Education degree with this UUID does not exist."
                }) from exc

        if major_uuid:
            try:
                major = Major.objects.get(uuid=major_uuid)
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "major_uuid": "Major with this UUID does not exist."
                }) from exc

        return CandidateQualification.objects.create(**validated_data)


class UpdateCandidateQualificationSerializer(CreateCandidateQualificationSerializer):
    """
    Specialized serializer for updating candidate qualifications.
    """

    class Meta(CreateCandidateQualificationSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        required_degree_uuid = validated_data.pop('required_degree_uuid', None)
        major_uuid = validated_data.pop('major_uuid', None)

        if required_degree_uuid:
            try:
                required_degree = EducationDegree.objects.get(
                    uuid=required_degree_uuid)
                validated_data['required_degree'] = required_degree
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "required_degree_uuid": "Education degree with this UUID does not exist."
                }) from exc

        if major_uuid:
            try:
                major = Major.objects.get(uuid=major_uuid)
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError({
                    "major_uuid": "Major with this UUID does not exist."
                }) from exc

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
