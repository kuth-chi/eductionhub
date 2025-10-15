"""
Resume/CV related serializers for User models
Handles Experience, Education, Skill, Language, Hobby, Reference, ProfileContact, Attachment, Letter
"""

from rest_framework import serializers

from api.serializers.organizations.organization_serializers import \
    OrganizationSerializer
from api.serializers.schools.base import SchoolSerializer
from api.serializers.social_platforms.platform_serializers import \
    PlatformSerializer
from api.serializers.user.profile import UserBasicSerializer
from schools.models.online_profile import Platform
from user.models.base import (Attachment, Education, Experience, Hobby,
                              Language, Letter, ProfileContact, Reference,
                              Skill)


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for file attachments"""

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file",
            "file_url",
            "name",
            "uploaded_at",
            "content_type",
        ]
        read_only_fields = ("id", "uploaded_at", "content_type", "file_url")

    def get_file_url(self, obj):
        """Return the full URL for the file"""
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class LetterSerializer(serializers.ModelSerializer):
    """Serializer for user letters/cover letters"""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = Letter
        fields = [
            "id",
            "user",
            "title",
            "content",
            "created_date",
            "updated_date",
            "is_active",
        ]
        read_only_fields = ("id", "user", "created_date", "updated_date")


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience entries"""

    organization = OrganizationSerializer(read_only=True)
    organization_uuid = serializers.UUIDField(
        write_only=True, required=False, allow_null=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,
    )

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "organization",
            "organization_uuid",
            "start_date",
            "end_date",
            "responsibilities",
            "attachments",
            "attachment_ids",
        ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        organization_uuid = validated_data.pop("organization_uuid", None)
        attachments = validated_data.pop("attachments", [])

        # Resolve organization by UUID if provided
        if organization_uuid:
            from organization.models import Organization
            try:
                organization = Organization.objects.get(uuid=organization_uuid)
                validated_data["organization"] = organization
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    {"organization_uuid": "Organization not found"})

        experience = Experience.objects.create(**validated_data)

        if attachments:
            experience.attachments.set(attachments)

        return experience

    def update(self, instance, validated_data):
        organization_uuid = validated_data.pop("organization_uuid", None)
        attachments = validated_data.pop("attachments", None)

        # Resolve organization by UUID if provided
        if organization_uuid:
            from organization.models import Organization
            try:
                organization = Organization.objects.get(uuid=organization_uuid)
                validated_data["organization"] = organization
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    {"organization_uuid": "Organization not found"})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if attachments is not None:
            instance.attachments.set(attachments)

        return instance


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education history entries"""

    institution = SchoolSerializer(read_only=True)
    institution_uuid = serializers.UUIDField(
        write_only=True, required=False, allow_null=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,
    )

    class Meta:
        model = Education
        fields = [
            "id",
            "institution",
            "institution_uuid",
            "degree",
            "start_date",
            "end_date",
            "description",
            "attachments",
            "attachment_ids",
        ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        institution_uuid = validated_data.pop("institution_uuid", None)
        attachments = validated_data.pop("attachments", [])

        # Resolve institution by UUID if provided
        if institution_uuid:
            from schools.models.school import School
            try:
                institution = School.objects.get(uuid=institution_uuid)
                validated_data["institution"] = institution
            except School.DoesNotExist:
                raise serializers.ValidationError(
                    {"institution_uuid": "School not found"})

        education = Education.objects.create(**validated_data)

        if attachments:
            education.attachments.set(attachments)

        return education

    def update(self, instance, validated_data):
        institution_uuid = validated_data.pop("institution_uuid", None)
        attachments = validated_data.pop("attachments", None)

        # Resolve institution by UUID if provided
        if institution_uuid:
            from schools.models.school import School
            try:
                institution = School.objects.get(uuid=institution_uuid)
                validated_data["institution"] = institution
            except School.DoesNotExist:
                raise serializers.ValidationError(
                    {"institution_uuid": "School not found"})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if attachments is not None:
            instance.attachments.set(attachments)

        return instance


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for user skills"""

    level_display = serializers.CharField(source='get_level_display', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,
    )

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "level",
            "level_display",
            "attachments",
            "attachment_ids",
        ]
        read_only_fields = ("id", "level_display")
    
    def validate_level(self, value):
        """Validate level is a valid choice"""
        if value is not None and value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("Invalid skill level. Must be 1 (Beginner), 2 (Intermediate), 3 (Advanced), or 4 (Expert).")
        return value


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for user languages"""

    level_display = serializers.CharField(source='get_level_display', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,
    )

    class Meta:
        model = Language
        fields = [
            "id",
            "name",
            "level",
            "level_display",
            "is_native",
            "attachments",
            "attachment_ids",
        ]
        read_only_fields = ("id", "level_display")
    
    def validate_level(self, value):
        """Validate level is a valid choice"""
        if value is not None and value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Invalid language proficiency level. Must be 1-5.")
        return value


class HobbySerializer(serializers.ModelSerializer):
    """Serializer for user hobbies"""

    class Meta:
        model = Hobby
        fields = [
            "id",
            "name",
        ]
        read_only_fields = ("id",)


class ReferenceSerializer(serializers.ModelSerializer):
    """Serializer for professional references"""

    company = OrganizationSerializer(read_only=True)
    company_uuid = serializers.UUIDField(
        write_only=True, required=False, allow_null=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Attachment.objects.all(),
        source="attachments",
        required=False,
    )

    class Meta:
        model = Reference
        fields = [
            "id",
            "name",
            "position",
            "company",
            "company_uuid",
            "relationship",
            "phone",
            "email",
            "attachments",
            "attachment_ids",
        ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        company_uuid = validated_data.pop("company_uuid", None)
        attachments = validated_data.pop("attachments", [])

        # Resolve company by UUID if provided
        if company_uuid:
            from organization.models import Organization
            try:
                company = Organization.objects.get(uuid=company_uuid)
                validated_data["company"] = company
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    {"company_uuid": "Organization not found"})

        reference = Reference.objects.create(**validated_data)

        if attachments:
            reference.attachments.set(attachments)

        return reference

    def update(self, instance, validated_data):
        company_uuid = validated_data.pop("company_uuid", None)
        attachments = validated_data.pop("attachments", None)

        # Resolve company by UUID if provided
        if company_uuid:
            from organization.models import Organization
            try:
                company = Organization.objects.get(uuid=company_uuid)
                validated_data["company"] = company
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    {"company_uuid": "Organization not found"})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if attachments is not None:
            instance.attachments.set(attachments)

        return instance


class ProfileContactSerializer(serializers.ModelSerializer):
    """Serializer for user contact profiles on various platforms"""

    platform = PlatformSerializer(read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Platform.objects.all(),
        source="platform",
        required=True,
    )

    class Meta:
        model = ProfileContact
        fields = [
            "uuid",
            "platform",
            "platform_id",
            "profile_url",
            "username",
            "privacy",
            "created_date",
            "updated_date",
            "is_active",
        ]
        read_only_fields = ("uuid", "created_date", "updated_date")
