
from rest_framework import serializers
from api.serializers.schools.college_serializers import CollegeSerializer
from schools.models.levels import SchoolBranch


class SchoolBranchSerializer(serializers.ModelSerializer):
    """Serializer for SchoolBranch model."""
    colleges = CollegeSerializer(many=True, read_only=True)
    class Meta:
        model = SchoolBranch
        fields = "__all__"
        read_only_fields = ['uuid', 'created_at']