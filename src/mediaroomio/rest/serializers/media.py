from rest_framework import serializers

from mediaroomio.models import MediaRoomConnector, MediaRoom


class MediaRoomSerializer(serializers.ModelSerializer):
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
