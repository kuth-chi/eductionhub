
from rest_framework import serializers
from schools.models.levels import SchoolBranch


class SchoolBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolBranch
        fields = "__all__"
        read_only_fields = ['uuid', 'created_at']