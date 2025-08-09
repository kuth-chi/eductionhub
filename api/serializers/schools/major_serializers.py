from rest_framework import serializers
from schools.models.levels import Major

class MajorSerializer(serializers.Serializer):
    """
    Serializer for Major model.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    school_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        return Major.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance