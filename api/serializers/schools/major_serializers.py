from typing import Iterable, List, Tuple, Union
from uuid import UUID

from django.db.models import Q
from rest_framework import serializers

from schools.models.levels import (College, DocumentRequirement,
                                   EducationDegree, Major)


def _split_ids_and_uuids(values: Iterable[Union[str, int, dict]]) -> Tuple[List[int], List[str]]:
    """
    Split incoming values into integer IDs and UUID strings.

    Accepts:
      - integers (ids)
      - numeric strings (ids)
      - uuid strings
      - small objects like {"id": 1} or {"uuid": "..."} or both
    """
    ids: List[int] = []
    uuids: List[str] = []
    for v in values or []:
        # Handle object inputs with id/uuid
        if isinstance(v, dict):
            vid = v.get("id")
            vuuid = v.get("uuid")
            if isinstance(vid, int):
                ids.append(vid)
                continue
            if isinstance(vid, str) and vid.isdigit():
                try:
                    ids.append(int(vid))
                    continue
                except ValueError:
                    pass
            if isinstance(vuuid, str):
                try:
                    UUID(vuuid)
                    uuids.append(vuuid)
                    continue
                except ValueError:
                    pass

        # accept numbers or numeric strings as IDs
        if isinstance(v, int) or (isinstance(v, str) and v.isdigit()):
            try:
                ids.append(int(v))
                continue
            except ValueError:
                pass
        # accept UUID-like strings
        if isinstance(v, str):
            try:
                UUID(v)
                uuids.append(v)
                continue
            except ValueError:
                # ignore malformed values
                pass
    return ids, uuids


class CollegeForMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ["id", "uuid", "name"]


class EducationDegreeForMajorSerializer(serializers.ModelSerializer):
    # Normalize name to work whether the model uses `name` or `degree_name`
    name = serializers.SerializerMethodField()

    class Meta:
        model = EducationDegree
        fields = ["id", "uuid", "name"]

    def get_name(self, obj):
        return getattr(obj, "name", None) or getattr(obj, "degree_name", None)


class DocumentRequirementForMajorSerializer(serializers.ModelSerializer):
    """Simplified serializer for document requirements within major context"""

    class Meta:
        model = DocumentRequirement
        fields = ["id", "uuid", "name", "description",
                  "accepted_formats", "is_mandatory", "is_active"]


class MajorSerializer(serializers.ModelSerializer):
    """Serializer for Major with flexible degree/college linkage.

    - Read: degrees and colleges are expanded as objects with id/uuid/name.
    - Write: accepts lists of IDs or UUID strings for degrees/colleges.
    """

    # Write-only inputs (accept list of ids or uuids); we reuse the same field names
    degrees = serializers.ListField(
        child=serializers.JSONField(), required=False, write_only=True)
    colleges = serializers.ListField(
        child=serializers.JSONField(), required=False, write_only=True)

    class Meta:
        model = Major
        fields = "__all__"
        read_only_fields = ("slug", "created_at", "updated_at")

    # Representation: expand M2M to list of objects
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["degrees"] = EducationDegreeForMajorSerializer(
            instance.degrees.all(), many=True).data
        rep["colleges"] = CollegeForMajorSerializer(
            instance.colleges.all(), many=True).data
        rep["document_requirements"] = DocumentRequirementForMajorSerializer(
            instance.document_requirements.filter(
                is_deleted=False, is_active=True),
            many=True
        ).data
        return rep

    def create(self, validated_data):
        degree_vals = validated_data.pop("degrees", [])
        college_vals = validated_data.pop("colleges", [])

        major = Major.objects.create(**validated_data)

        if degree_vals:
            deg_ids, deg_uuids = _split_ids_and_uuids(degree_vals)
            degree_qs = EducationDegree.objects.filter(
                (Q(id__in=deg_ids) | Q(uuid__in=deg_uuids)),
                is_active=True,
                is_deleted=False,
            )
            major.degrees.set(degree_qs)

        if college_vals:
            col_ids, col_uuids = _split_ids_and_uuids(college_vals)
            college_qs = College.objects.filter(
                (Q(id__in=col_ids) | Q(uuid__in=col_uuids)),
                is_active=True,
                is_deleted=False,
            )
            major.colleges.set(college_qs)

        return major

    def update(self, instance, validated_data):
        degree_vals = validated_data.pop("degrees", None)
        college_vals = validated_data.pop("colleges", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if degree_vals is not None:
            deg_ids, deg_uuids = _split_ids_and_uuids(degree_vals)
            degree_qs = EducationDegree.objects.filter(
                (Q(id__in=deg_ids) | Q(uuid__in=deg_uuids)),
                is_active=True,
                is_deleted=False,
            )
            instance.degrees.set(degree_qs)

        if college_vals is not None:
            col_ids, col_uuids = _split_ids_and_uuids(college_vals)
            college_qs = College.objects.filter(
                (Q(id__in=col_ids) | Q(uuid__in=col_uuids)),
                is_active=True,
                is_deleted=False,
            )
            instance.colleges.set(college_qs)

        return instance
