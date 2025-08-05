from rest_framework import serializers
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

# Application
from api.serializers.schools.branch import SchoolBranchSerializer
from schools.models.school import School, SchoolType
from schools.models.online_profile import PlatformProfile, Platform
from schools.models.levels import EducationalLevel
from schools.models.levels import (
    College,
    Major,
    EducationDegree,
    SchoolDegreeOffering,
    SchoolCollegeAssociation,
    SchoolMajorOffering,
)
from schools.models.scholarship import (Scholarship, ScholarshipType)
from schools.models.school import (
    FieldOfStudy,
    SchoolScholarship,
    SchoolCustomizeButton,
    SchoolBranch,
    Address,
    PhoneContact,
)


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

        # If it's a string, return as-is
        if isinstance(value, str):
            return value

        # If it's an ImageField instance, check if it has a file
        if hasattr(value, "url"):
            try:
                # Try to access the URL - this will fail if no file is associated
                return value.url
            except ValueError:
                # If no file is associated, return None
                return None

        return value

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

class EducationalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalLevel
        fields = "__all__"


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


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model"""

    logo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    cover_image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)

    type = SchoolTypeSerializer(many=True, read_only=True)
    educational_levels = EducationalLevelSerializer(many=True, read_only=True)
    platform_profiles = PlatformProfileSerializer(source="platform_profiles_school", many=True, read_only=True)

    type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=SchoolType.objects.all(),
        required=False,
        source="type",
    )
    educational_level_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=EducationalLevel.objects.all(),
        required=False,
        source="educational_levels",
    )

    branches = SchoolBranchSerializer(many=True, read_only=True)
    branch_count = serializers.SerializerMethodField(read_only=True)
    college_count = serializers.SerializerMethodField(read_only=True)
    major_count = serializers.SerializerMethodField(read_only=True)
    degree_count = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        def resolve_image_url(image_field):
            if not image_field:
                return None
            try:
                return image_field.url  # standard case
            except ValueError:
                try:
                    return default_storage.url(str(image_field))  # fallback to raw path
                except Exception:
                    return None

        data["logo"] = resolve_image_url(instance.logo)
        data["cover_image"] = resolve_image_url(instance.cover_image)

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
        return SchoolBranch.objects.filter(school=obj).count()

    def get_college_count(self, obj):
        from schools.models.levels import SchoolCollegeAssociation
        return SchoolCollegeAssociation.objects.filter(school=obj).count()

    def get_major_count(self, obj):
        from schools.models.levels import SchoolMajorOffering
        return SchoolMajorOffering.objects.filter(school=obj).count()

    def get_degree_count(self, obj):
        from schools.models.levels import SchoolDegreeOffering
        return SchoolDegreeOffering.objects.filter(school=obj).count()

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
            "self_data",
            "type",
            "educational_levels",
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
            educational_levels_data = validated_data.pop("educational_levels", [])
            school = School.objects.create(**validated_data)
            school.type.set(types_data)
            school.educational_levels.set(educational_levels_data)
            return school
        except Exception as e:
            print(f"Error creating school: {e}")
            import traceback
            traceback.print_exc()
            raise

    def update(self, instance, validated_data):
        print(f"SchoolSerializer.update called with validated_data: {validated_data}")

        types_data = validated_data.pop("type", [])
        educational_levels_data = validated_data.pop("educational_levels", [])

        logo_path = validated_data.pop("logo", None)
        cover_image_path = validated_data.pop("cover_image", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if logo_path is not None:
            instance.logo = logo_path if logo_path else None

        if cover_image_path is not None:
            instance.cover_image = cover_image_path if cover_image_path else None

        if types_data:
            instance.type.set(types_data)
        if educational_levels_data:
            instance.educational_levels.set(educational_levels_data)

        instance.save()
        print(f"School saved. Logo: {instance.logo}, Cover: {instance.cover_image}")

        return instance


# --- Additional Serializers for full API coverage ---


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = "__all__"


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = "__all__"


class EducationDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDegree
        fields = "__all__"


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


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = "__all__"
