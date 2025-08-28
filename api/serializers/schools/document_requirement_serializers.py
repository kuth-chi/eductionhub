# api/serializers/schools/document_requirement_serializers.py
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from schools.models.levels import DocumentRequirement, Major


class MajorForDocumentRequirementSerializer(serializers.ModelSerializer):
    """Serializer for Major model when used in document requirements"""

    class Meta:
        model = Major
        fields = ("id", "uuid", "name", "code", "is_active")


class DocumentRequirementSerializer(serializers.ModelSerializer):
    """Serializer for DocumentRequirement model"""

    major = MajorForDocumentRequirementSerializer(read_only=True)
    major_uuid = serializers.UUIDField(
        write_only=True, required=False, allow_null=True)

    class Meta:
        model = DocumentRequirement
        fields = [
            "id",
            "uuid",
            "name",
            "description",
            "accepted_formats",
            "major",
            "major_uuid",
            "is_mandatory",
            "is_active",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ("id", "uuid", "created_at", "updated_at")

    def create(self, validated_data):
        major_uuid = validated_data.pop('major_uuid', None)

        if major_uuid:
            try:
                major = Major.objects.get(uuid=major_uuid)
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError(
                    {"major_uuid": "Major with this UUID does not exist."}
                ) from exc

        return super().create(validated_data)

    def update(self, instance, validated_data):
        major_uuid = validated_data.pop('major_uuid', None)

        if major_uuid:
            try:
                major = Major.objects.get(uuid=major_uuid)
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError(
                    {"major_uuid": "Major with this UUID does not exist."}
                ) from exc

        return super().update(instance, validated_data)


class CreateDocumentRequirementSerializer(serializers.ModelSerializer):
    """Serializer for creating document requirements"""

    major_uuid = serializers.UUIDField(required=True)  # Make major required

    class Meta:
        model = DocumentRequirement
        fields = [
            "name",
            "description",
            "accepted_formats",
            "major_uuid",
            "is_mandatory",
            "is_active"
        ]

    def create(self, validated_data):
        major_uuid = validated_data.pop('major_uuid', None)

        if not major_uuid:
            raise serializers.ValidationError(
                {"major_uuid": "Major is required for document requirements."})

        try:
            major = Major.objects.get(
                uuid=major_uuid, is_active=True, is_deleted=False)
            validated_data['major'] = major
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                {"major_uuid": "Major with this UUID does not exist or is not active."}
            ) from exc

        return DocumentRequirement.objects.create(**validated_data)


class UpdateDocumentRequirementSerializer(CreateDocumentRequirementSerializer):
    """Serializer for updating document requirements"""

    class Meta(CreateDocumentRequirementSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        major_uuid = validated_data.pop('major_uuid', None)

        if major_uuid:
            try:
                major = Major.objects.get(uuid=major_uuid)
                validated_data['major'] = major
            except ObjectDoesNotExist as exc:
                raise serializers.ValidationError(
                    {"major_uuid": "Major with this UUID does not exist."}
                ) from exc

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
