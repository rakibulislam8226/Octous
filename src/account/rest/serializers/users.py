from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from common.variable import versatile_image_size
from core.models import User


class UserMinReadOnlySerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=versatile_image_size,
        required=False,
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "uid",
            "slug",
            "name",
            "email",
            "phone",
            "image",
            "gender",
        ]
        read_only_fields = fields
