from rest_framework import serializers
from user.models.profile import Profile
from user.models.base import User


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")


class CountrySimpleSerializer(serializers.Serializer):
    """Simple serializer for Country foreign key"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    flag_emoji = serializers.CharField(required=False, allow_blank=True)


class StateSimpleSerializer(serializers.Serializer):
    """Simple serializer for State foreign key"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    country = CountrySimpleSerializer()


class CitySimpleSerializer(serializers.Serializer):
    """Simple serializer for City foreign key"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    state = StateSimpleSerializer()


class ProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    country = CountrySimpleSerializer(read_only=True)
    state = StateSimpleSerializer(read_only=True)
    city = CitySimpleSerializer(read_only=True)
    
    # Writable fields for foreign keys (use IDs for updates)
    country_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    state_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    city_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Profile
        fields = [
            "uuid",
            "user",
            "photo",
            "gender",
            "occupation",
            "timezone",
            # New personal fields
            "phone",
            "date_of_birth",
            # Address fields (simple text)
            "address_line1",
            "address_line2",
            "postal_code",
            # Address fields (geo models)
            "country",
            "country_id",
            "state",
            "state_id",
            "city",
            "city_id",
            # Timestamps
            "created_date",
            "updated_date",
        ]
        read_only_fields = ("uuid", "created_date", "updated_date", "user")
    
    def update(self, instance, validated_data):
        """Handle updates including foreign key IDs"""
        # Extract foreign key IDs
        country_id = validated_data.pop('country_id', None)
        state_id = validated_data.pop('state_id', None)
        city_id = validated_data.pop('city_id', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update foreign keys if provided
        if country_id is not None:
            if country_id == 0:  # Allow clearing
                instance.country = None
            else:
                from geo.models import Country
                try:
                    instance.country = Country.objects.get(id=country_id)
                except Country.DoesNotExist:
                    pass
        
        if state_id is not None:
            if state_id == 0:  # Allow clearing
                instance.state = None
            else:
                from geo.models import State
                try:
                    instance.state = State.objects.get(id=state_id)
                except State.DoesNotExist:
                    pass
        
        if city_id is not None:
            if city_id == 0:  # Allow clearing
                instance.city = None
            else:
                from geo.models import City
                try:
                    instance.city = City.objects.get(id=city_id)
                except City.DoesNotExist:
                    pass
        
        instance.save()
        return instance
