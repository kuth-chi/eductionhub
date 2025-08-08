from rest_framework import serializers
from schools.models.school import School


class SimpleSchoolSerializer(serializers.ModelSerializer):
    """Minimal serializer for testing"""

    class Meta:
        model = School
        fields = (
            "pk",
            "uuid",
            "name",
            "local_name",
            "logo",
            "cover_image",
            "short_name",
            "code",
            "description",
            "founder",
            "president",
            "established",
            "street_address",
            "address_line_2",
            "box_number",
            "postal_code",
            "country",
            "state",
            "city",
            "village",
            "location",
            "motto",
            "tuition",
            "endowment",
            "created_date",
            "updated_date",
            "slug",
            "is_active",
            "self_data",
        )
