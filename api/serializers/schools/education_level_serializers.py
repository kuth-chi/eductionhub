# api/serializers/schools/education_level_serializers.py
from rest_framework import serializers

from schools.models.levels import EducationalLevel

class EducationalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalLevel
        fields = "__all__"