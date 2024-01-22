from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from common.variable import versatile_image_size
from mediaroomio.models import MediaRoomConnector, MediaRoom


class MediaRoomSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=versatile_image_size,
        required=False,
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
    )

    class Meta:
        model = MediaRoom
        fields = [
            "uid",
            "image",
            "file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class MediaRoomConnectorSerializer(serializers.ModelSerializer):
    media_room = MediaRoomSerializer(read_only=True)

    class Meta:
        model = MediaRoomConnector
        fields = [
            "uid",
            "media_room",
        ]
        read_only_fields = fields
