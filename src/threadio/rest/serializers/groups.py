import json

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from versatileimagefield.serializers import VersatileImageFieldSerializer

from common.variable import versatile_image_size
from core.choices import UserStatus
from core.models import User
from core.rest.serializers.users import UserMinSerializer
from mediaroomio.models import MediaRoom
from mediaroomio.rest.serializers.media import MediaRoomSerializer
from threadio.choices import GroupParticipantRoleChoices
from threadio.models import Group, GroupParticipant


class GroupListSerializer(serializers.ModelSerializer):
    banner = MediaRoomSerializer(read_only=True, allow_null=True)
    banner_image = VersatileImageFieldSerializer(
        sizes=versatile_image_size,
        required=False,
        allow_null=True,
        allow_empty_file=True,
        write_only=True,
    )
    created_by = UserMinSerializer(read_only=True)
    participants = UserMinSerializer(read_only=True, many=True)
    participants_phone_numbers = serializers.CharField(
        write_only=True,
        help_text="Use participants phone number in a array like this '['+88017111111110,'+8801521111111']', make sure make this list into string as we string this as a string and later covert to the list.",
    )

    def validate_participants_phone_numbers(self, data):
        import ast

        data: list = ast.literal_eval(data)
        participants_user_instance = []

        for user_phone in data:
            try:
                participants_user_instance.append(User.objects.get(phone=user_phone))
            except User.DoesNotExist:
                raise ValidationError(f"User with {user_phone} does not exist")

        return participants_user_instance

    class Meta:
        model = Group
        fields = [
            "name",
            "uid",
            "slug",
            "description",
            "banner",
            "banner_image",
            "created_by",
            "status",
            "is_need_approval",
            "participants",
            "participants_phone_numbers",
            "disable_till",
            "is_group",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "uid", "created_at", "updated_at"]

    def validate_name(self, data):
        if Group.objects.filter(name=data).exclude(name="").exists():
            raise ValidationError(detail="Group with this name already exists")
        return data

    def create(self, validated_data):
        from django.core.files.uploadedfile import InMemoryUploadedFile

        participants = validated_data.pop("participants_phone_numbers", None)
        banner = validated_data.pop("banner_image", None)
        current_user = self.context["request"].user
        if banner and isinstance(banner, InMemoryUploadedFile):
            validated_data["banner"] = MediaRoom.objects.create(image=banner)

        validated_data["created_by"] = current_user
        instance: Group = super().create(validated_data)
        GroupParticipant.objects.create(
            group=instance,
            user=current_user,
            role=GroupParticipantRoleChoices.OWNER,
        )

        instance.participants.add(*participants)
        return instance
