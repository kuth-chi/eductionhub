from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from rest_framework import serializers

# Application
from api.serializers.schools.branch_serializers import SchoolBranchSerializer
from api.serializers.schools.degree_serializers import \
    EducationDegreeSerializer
from api.serializers.schools.education_level_serializers import \
    EducationalLevelSerializer
from schools.models.levels import (College, EducationalLevel, EducationDegree,
                                   Major, SchoolCollegeAssociation,
                                   SchoolDegreeOffering, SchoolMajorOffering)
from schools.models.online_profile import Platform, PlatformProfile
from schools.models.scholarship import Scholarship, ScholarshipType
from schools.models.school import (Address, FieldOfStudy, School,
                                   SchoolBranchContactInfo,
                                   SchoolCustomizeButton, SchoolScholarship,
                                   SchoolType)


class HybridImageField(serializers.ImageField):
    """
    A hybrid field that can handle both file uploads and URL strings.
    For file uploads, it behaves like a normal ImageField.
    For URL strings, it stores the URL as-is in a custom field.
    """

    def to_internal_value(self, data):
        if data is None:
            return None

        # If it's a file upload, handle normally
        if isinstance(data, UploadedFile) or hasattr(data, "read"):
            return super().to_internal_value(data)

        # If it's a string (URL), return as-is for handling in update method
        if isinstance(data, str):
            return data

        # For other types, try normal validation
        return super().to_internal_value(data)

    def to_representation(self, value):
        """
        Override to handle ImageField instances that don't have files
        """
        if value is None:
            return None

        # If it's a plain string path/URL, return as-is
        if isinstance(value, str):
            return value

        # If it's a Django FieldFile (ImageFieldFile/FileField), return its name (relative path)
        if isinstance(value, FieldFile):
            name = getattr(value, "name", "")
            return name or None

        # Fallback: don't attempt to access .url which can raise when file is missing
        return None

    def get_attribute(self, instance):
        """
        Override to handle both file objects and string URLs
        """
        value = super().get_attribute(instance)
        if isinstance(value, str):
            # If it's a string URL, return it directly
            return value
        return value


# --- Additional Serializers for full API coverage ---
class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = (
            "id",
            "uuid",
            "name",
            "short_name",
            "url",
            "icon",
            "created_date",
            "updated_date",
            "is_active",
        )


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = (
            "id",
            "uuid",
            "type",
            "description",
            "icon",
            "created_date",
            "updated_date",
            "is_active",
        )


class PlatformProfileSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
    school = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PlatformProfile
        fields = (
            "id",
            "uuid",
            "profile_url",
            "username",
            "platform",
            "school",
            "created_date",
            "updated_date",
            "is_active",
        )


class SchoolListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer enriched for client-side filtering/sorting."""

    # Relateds needed for filters
    type = SchoolTypeSerializer(many=True, read_only=True)
    educational_levels = EducationalLevelSerializer(many=True, read_only=True)

    # Counts (use annotations if present; fallback to queries)
    branch_count = serializers.SerializerMethodField()
    college_count = serializers.SerializerMethodField(read_only=True)
    major_count = serializers.SerializerMethodField(read_only=True)
    degree_count = serializers.SerializerMethodField(read_only=True)

    # New: locations array field
    locations = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            "pk",
            "uuid",
            "slug",
            "name",
            "local_name",
            "short_name",
            "logo",
            "cover_image",
            "location",
            "locations",  # <-- new field
            "created_date",
            "updated_date",
            "type",
            "educational_levels",
            # Filter feature fields
            "colleges",
            "degrees",
            "majors",
            "branch_addresses",
            "branch_count",
            "college_count",
            "major_count",
            "degree_count",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        def resolve_image_path(image_field):
            if not image_field:
                return None
            # FieldFile variant: return stored relative path without touching storage/url
            if isinstance(image_field, FieldFile):
                name = getattr(image_field, "name", "")
                return name or None
            # Plain string path/URL
            if isinstance(image_field, str):
                return image_field or None
            return None

        # Ensure image fields are safe and consistent
        data["logo"] = resolve_image_path(getattr(instance, "logo", None))
        data["cover_image"] = resolve_image_path(
            getattr(instance, "cover_image", None))

        # Add locations array: school location + branch locations
        data["locations"] = self.get_locations(instance)
        return data

    def _is_valid_location(self, location):
        """Helper to validate location string format."""
        return isinstance(location, str) and "," in location

    def get_locations(self, obj):
        locations = []
        # Add school's own location if present and valid
        if obj.location and self._is_valid_location(obj.location):
            locations.append(obj.location.strip())
        # Add branch locations
        branch_qs = getattr(obj, "school_branches", None)
        if branch_qs:
            for branch in branch_qs.all():
                loc = getattr(branch, "location", None)
                if loc and self._is_valid_location(loc):
                    locations.append(loc.strip())
        # Remove duplicates and empty
        return sorted(list({l for l in locations if l}))

    def get_branch_count(self, obj):
        return getattr(obj, "branch_count", obj.school_branches.count())

    def get_college_count(self, obj):
        annotated = getattr(obj, "college_count", None)
        if isinstance(annotated, int):
            return annotated
        # Unique colleges linked to any branch of this school, or via associations
        return (
            College.objects.filter(
                Q(branches__school=obj) | Q(school_associations__school=obj)
            )
            .distinct()
            .count()
        )

    def get_major_count(self, obj):
        annotated = getattr(obj, "major_count", None)
        if isinstance(annotated, int):
            return annotated
        # Unique majors linked via colleges on branches or explicit offerings
        return (
            Major.objects.filter(
                Q(colleges__branches__school=obj) | Q(
                    school_offerings__school=obj)
            )
            .distinct()
            .count()
        )

    def get_degree_count(self, obj):
        annotated = getattr(obj, "degree_count", None)
        if isinstance(annotated, int):
            return annotated
        # Unique degrees linked via colleges on branches or explicit offerings
        return (
            EducationDegree.objects.filter(
                Q(colleges__branches__school=obj) | Q(
                    school_offerings__school=obj)
            )
            .distinct()
            .count()
        )

    # --- Filter feature fields ---
    colleges = serializers.SerializerMethodField()
    degrees = serializers.SerializerMethodField()
    majors = serializers.SerializerMethodField()
    branch_addresses = serializers.SerializerMethodField()

    def _unique_sorted(self, items):
        return sorted(list({i for i in items if i}))

    def get_colleges(self, obj):
        qs = SchoolCollegeAssociation.objects.filter(
            school=obj).select_related("college")
        names = [assoc.college.name for assoc in qs if getattr(
            assoc, "college", None)]
        return self._unique_sorted(names)

    def get_degrees(self, obj):
        qs = SchoolDegreeOffering.objects.filter(
            school=obj).select_related("degree")
        names = [off.degree.degree_name for off in qs if getattr(
            off, "degree", None)]
        return self._unique_sorted(names)

    def get_majors(self, obj):
        qs = SchoolMajorOffering.objects.filter(
            school=obj).select_related("major")
        names = [off.major.name for off in qs if getattr(off, "major", None)]
        return self._unique_sorted(names)

    def get_branch_addresses(self, obj):
        addresses = list(obj.school_branches.values_list("address", flat=True))
        return self._unique_sorted(addresses)


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model"""

    # Accept either uploaded files (multipart) or string paths/URLs (JSON)
    logo = HybridImageField(
        required=False, allow_null=True, allow_empty_file=True)
    cover_image = HybridImageField(
        required=False, allow_null=True, allow_empty_file=True)

    platform_profiles = PlatformProfileSerializer(
        source="platform_profiles_school", many=True, read_only=True)

    type = SchoolTypeSerializer(many=True, read_only=True)
    type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=SchoolType.objects.all(),
        required=False,
        source="type",
    )
    educational_levels = EducationalLevelSerializer(many=True, read_only=True)
    educational_level_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=EducationalLevel.objects.all(),
        required=False,
        source="educational_levels",
    )

    # Use the correct related_name from SchoolBranch model
    branches = SchoolBranchSerializer(
        source="school_branches", many=True, read_only=True)
    branch_count = serializers.SerializerMethodField()
    college_count = serializers.SerializerMethodField(read_only=True)
    major_count = serializers.SerializerMethodField(read_only=True)
    degree_levels = EducationDegreeSerializer(many=True, read_only=True)
    degree_count = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        def resolve_image_path(image_field):
            if not image_field:
                return None
            # FieldFile variant: return stored relative path without touching storage/url
            if isinstance(image_field, FieldFile):
                name = getattr(image_field, "name", "")
                return name or None
            # Stored path or plain string
            if isinstance(image_field, str):
                return image_field or None
            return None

        data["logo"] = resolve_image_path(getattr(instance, "logo", None))
        data["cover_image"] = resolve_image_path(
            getattr(instance, "cover_image", None))

        return data

    def to_internal_value(self, data):
        if "established" in data and data["established"] == 0:
            data = data.copy()
            data["established"] = None

        for key in ["type", "platforms", "organization", "degree_levels"]:
            if key in data and isinstance(data[key], (dict, list)):
                data = data.copy()
                data.pop(key, None)

        return super().to_internal_value(data)

    def validate(self, attrs):
        return attrs

    def get_branch_count(self, obj):
        return obj.school_branches.count()

    def get_college_count(self, obj):
        # Unique colleges linked to any branch of this school, or via associations
        return (
            College.objects.filter(
                Q(branches__school=obj) | Q(school_associations__school=obj)
            )
            .distinct()
            .count()
        )

    def get_major_count(self, obj):
        # Unique majors linked via colleges on branches or explicit offerings
        return (
            Major.objects.filter(
                Q(colleges__branches__school=obj) | Q(
                    school_offerings__school=obj)
            )
            .distinct()
            .count()
        )

    def get_degree_count(self, obj):
        # Unique degrees linked via colleges on branches or explicit offerings
        return (
            EducationDegree.objects.filter(
                Q(colleges__branches__school=obj) | Q(
                    school_offerings__school=obj)
            )
            .distinct()
            .count()
        )

    class Meta:
        model = School
        fields = (
            "pk",
            "uuid",
            "name",
            "local_name",
            "logo",
            "cover_image",
            "short_name",
            "code",
            "description",
            "founder",
            "president",
            "established",
            "street_address",
            "address_line_2",
            "box_number",
            "postal_code",
            "country",
            "state",
            "city",
            "village",
            "location",
            "motto",
            "tuition",
            "endowment",
            "created_date",
            "updated_date",
            "slug",
            "is_active",
            # "self_data",
            "type",
            "educational_levels",
            "degree_levels",
            "platform_profiles",
            "type_ids",
            "educational_level_ids",
            "branch_count",
            "branches",
            "college_count",
            "major_count",
            "degree_count",
        )

    def create(self, validated_data):
        try:
            types_data = validated_data.pop("type", [])
            educational_levels_data = validated_data.pop(
                "educational_levels", [])
            school = School.objects.create(**validated_data)
            school.type.set(types_data)
            school.educational_levels.set(educational_levels_data)
            return school
        except Exception as e:
            # Surface as validation error (400) instead of 500 to help clients diagnose issues
            raise serializers.ValidationError({
                "detail": f"Failed to create school: {str(e)}"
            }) from e

    def update(self, instance, validated_data):
        print(
            f"SchoolSerializer.update called with validated_data: {validated_data}")

        types_data = validated_data.pop("type", [])
        educational_levels_data = validated_data.pop("educational_levels", [])

        logo_path = validated_data.pop("logo", None)
        cover_image_path = validated_data.pop("cover_image", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Support both UploadedFile and string (stored path/URL) assignments
        if logo_path is not None:
            instance.logo = logo_path or None

        if cover_image_path is not None:
            instance.cover_image = cover_image_path or None

        if types_data:
            instance.type.set(types_data)
        if educational_levels_data:
            instance.educational_levels.set(educational_levels_data)

        instance.save()
        print(
            f"School saved. Logo: {instance.logo}, Cover: {instance.cover_image}")

        return instance


# --- Additional Serializers for full API coverage ---
class SchoolDegreeOfferingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolDegreeOffering
        fields = "__all__"


class SchoolCollegeAssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolCollegeAssociation
        fields = "__all__"


class SchoolMajorOfferingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolMajorOffering
        fields = "__all__"


class FieldOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfStudy
        fields = "__all__"


class ScholarshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipType
        fields = "__all__"


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = "__all__"


class SchoolScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolScholarship
        fields = "__all__"


class SchoolCustomizeButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolCustomizeButton
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class SchoolBranchContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolBranchContactInfo
        fields = "__all__"
