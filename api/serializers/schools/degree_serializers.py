#  api/serializers/schools/degree_level_serializers.py
from rest_framework import serializers

from api.serializers.schools.education_level_serializers import \
    EducationalLevelSerializer
from schools.models.levels import EducationalLevel, EducationDegree


# Define parent degree serializer
class ParentEducationDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDegree
        fields = "__all__"


class EducationDegreeSerializer(serializers.ModelSerializer):
    parent_degree = ParentEducationDegreeSerializer(read_only=True)
    level = EducationalLevelSerializer(read_only=True)
    level_uuid = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EducationalLevel.objects.filter(
            is_active=True, is_deleted=False),
        source='level',
        write_only=True,
        required=False,
        allow_null=True
    )
    parent_degree_uuid = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EducationDegree.objects.filter(
            is_active=True, is_deleted=False),
        source='parent_degree',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = EducationDegree
        fields = '__all__'
        read_only_fields = ['created_date', 'updated_date']

    def to_representation(self, instance):
        """Customize the output representation"""
        representation = super().to_representation(instance)

        # Add level and parent_degree UUIDs for easier frontend handling
        if instance.level:
            representation['level_uuid'] = str(instance.level.uuid)
        if instance.parent_degree:
            representation['parent_degree_uuid'] = str(
                instance.parent_degree.uuid)

        return representation
