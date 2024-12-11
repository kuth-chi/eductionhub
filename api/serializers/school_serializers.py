from rest_framework import serializers

# Application
from schools.models.schoolsModel import School, SchoolType
from schools.models.OnlineProfile import PlatformProfile, Platform
from schools.models.levels import EducationalLevel


class EducationalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalLevel
        fields = ("__all__")


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ("name", "url", "uuid", "icon")


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = ("type", "description", "icon")


class PlatformProfileSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)  
    school = serializers.PrimaryKeyRelatedField(read_only=True)  

    class Meta:
        model = PlatformProfile
        fields = ("profile_url", "username", "platform", "school", "uuid", "created_date", "updated_date")



class SchoolSerializer(serializers.ModelSerializer):
    type = SchoolTypeSerializer(many=True, read_only=True)
    educational_levels = EducationalLevelSerializer(many=True, read_only=True)
    platform_profiles = PlatformProfileSerializer(
        source="platform_profiles_school", many=True, read_only=True
    )  # Use related_name "platform_profiles_school"

    class Meta:
        model = School
        fields = (
            'pk', 'uuid', 'name', 'local_name', 'logo', 'cover_image', 'short_name', 
            'founder', 'president', 'established', 'location', 'created_date', 
            'updated_date', 'slug', 'type', 'educational_levels', 'platform_profiles'
        )

    def create(self, validated_data):
        types_data = validated_data.pop('type', [])
        school = School.objects.create(**validated_data)
        school.type.set(types_data)
        return school

    def update(self, instance, validated_data):
        types_data = validated_data.pop('type', [])
        instance = super().update(instance, validated_data)
        instance.type.set(types_data)
        return instance
