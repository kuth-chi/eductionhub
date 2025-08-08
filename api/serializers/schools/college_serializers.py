# api/serializers/schools/college_serializers.py
from rest_framework import serializers
from schools.models.levels import College

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = "__all__"