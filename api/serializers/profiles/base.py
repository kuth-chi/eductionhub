# api/serializers/profiles/serializers.py
from rest_framework import serializers
from user.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'uuid',
            'user',  # user ID
            'user_full_name',  # custom full name field
            'photo',
            'gender',
            'occupation',
            'timezone',
            'created_date',
            'updated_date',
        ]
        read_only_fields = ['uuid', 'created_date', 'updated_date']

    def get_user_full_name(self, obj):
        if obj.user:
            first_name = obj.user.first_name or ""
            last_name = obj.user.last_name or ""
            if first_name or last_name:
                return f"{first_name} {last_name}".strip()
            return obj.user.username
        return None
