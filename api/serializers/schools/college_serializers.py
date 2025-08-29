# api/serializers/schools/college_serializers.py
from rest_framework import serializers

from schools.models.levels import College, EducationDegree, Major
from schools.models.school import School, SchoolBranch


# Define School for Branch serializer
class SchoolForBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("id", "uuid", "name", "local_name", "is_active")

# Define School Branch Serializer Class for College


class SchoolBranchForCollegeSerializer(serializers.ModelSerializer):
    school = SchoolForBranchSerializer(read_only=True)

    class Meta:
        model = SchoolBranch
        fields = ("id", "uuid", "name", "school", "is_active")

# Define College Serializer Class


class EducationDegreeForCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDegree
        fields = ("id", "uuid", "degree_name", "is_active")


class MajorForCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ("id", "uuid", "name", "code", "is_active")


class CollegeSerializer(serializers.ModelSerializer):
    branches = SchoolBranchForCollegeSerializer(many=True, read_only=True)
    degrees = EducationDegreeForCollegeSerializer(many=True, read_only=True)
    majors = MajorForCollegeSerializer(many=True, read_only=True)

    class Meta:
        model = College
        fields = "__all__"
