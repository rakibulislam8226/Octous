import json

from django.db.models import Case, When, Value, BooleanField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from versatileimagefield.serializers import VersatileImageFieldSerializer

from account.rest.serializers.users import UserMinReadOnlySerializer
from common.variable import versatile_image_size
from core.choices import UserStatus
from core.models import User
from core.rest.serializers.users import UserMinSerializer
from mediaroomio.models import MediaRoom
from mediaroomio.rest.serializers.media import MediaRoomSerializer
from threadio.choices import GroupParticipantRoleChoices, GroupParticipantChoices
from threadio.models import ChatGroup, ChatGroupParticipant, Thread, ThreadRead


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
        model = ChatGroup
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
        if ChatGroup.objects.filter(name=data).exclude(name="").exists():
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

        # create chat group
        instance: ChatGroup = super().create(validated_data)

        # add the owner(current user) of this group as role owner
        ChatGroupParticipant.objects.create(
            group=instance,
            user=current_user,
            status=GroupParticipantChoices.ACTIVE,
            role=GroupParticipantRoleChoices.OWNER,
        )

        # add other selected members in this group
        ChatGroupParticipant.objects.bulk_create(
            [
                ChatGroupParticipant(
                    user=user, group=instance, status=GroupParticipantChoices.ACTIVE
                )
                for user in participants
                if not ChatGroupParticipant.objects.filter(
                    user=user, group=instance
                ).exists()
            ]
        )

        return instance


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = "__all__"


class ThreadReadMinReadOnlySerializer(serializers.Serializer):
    is_read = serializers.BooleanField(read_only=True)
    user = UserMinReadOnlySerializer(read_only=True)


class RecursiveThreadSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = PrivateThreadListSerializer(instance, context=self.context)
        data = serializer.data

        # Check if the instance has replies
        if instance.replies.exists():
            replies_serializer = self.__class__(
                instance.replies.all(), many=True, context=self.context
            )
            data["replies"] = replies_serializer.data

        return data


class PrivateThreadParentListSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=versatile_image_size,
        required=False,
        allow_null=True,
        allow_empty_file=True,
        write_only=True,
    )
    file = serializers.FileField(allow_empty_file=True, allow_null=True, required=False)
    media_room = MediaRoomSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "file",
            "image",
            "media_room",
        ]
        read_only_fields = ["uid"]


class PrivateThreadListSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=versatile_image_size,
        required=False,
        allow_null=True,
        allow_empty_file=True,
        write_only=True,
    )
    file = serializers.FileField(
        allow_empty_file=True, allow_null=True, required=False, write_only=True
    )
    media_room = MediaRoomSerializer(read_only=True)
    replies = RecursiveThreadSerializer(many=True, read_only=True)
    parent = serializers.SlugRelatedField(
        queryset=Thread.objects.filter(),
        slug_field="uid",
        required=False,
        allow_null=True,
        allow_empty=True,
    )
    sender = UserMinReadOnlySerializer(read_only=True)
    is_read = serializers.BooleanField(default=False, read_only=True)
    read_users = ThreadReadMinReadOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "file",
            "image",
            "media_room",
            "replies",
            "parent",
            "sender",
            "is_read",
            "created_at",
            "updated_at",
            "read_users",
        ]
        read_only_fields = ["uid"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print()
        data["parent"] = (
            PrivateThreadParentListSerializer(instance.parent).data
            if instance.parent
            else None
        )
        return data

    def validate(self, attrs):
        logged_in_user = self.context["request"].user
        group = self.context["view"].kwargs.get("chat_group_uid", None)

        if group is None:
            raise ValidationError({"detail": "Group uuid is required."})

        group_uid = self.context["view"].kwargs.get("chat_group_uid")

        # check if user have permission to this group chat or not
        group = ChatGroup.objects.get(uid=group_uid)
        if not group.chatgroupparticipant_set.filter(user=logged_in_user).exists():
            raise ValidationError({"detail": "You do not have any permission."})

        attrs["group"] = group
        attrs["sender"] = logged_in_user
        return attrs

    def create(self, validated_data):
        file = validated_data.pop("file", None)
        image = validated_data.pop("image", None)
        user = self.context["request"].user
        if not (image is None and file is None):
            validated_data["media_room"] = MediaRoom.objects.create(
                file=file, image=image
            )

        instance: Thread = super().create(validated_data)

        bulk_data = [
            ThreadRead(
                thread=instance,
                user=group_participant.user,
                group=instance.group,
                is_read=True if group_participant.user == user else False,
            )
            for group_participant in ChatGroupParticipant.objects.filter(
                group=instance.group, status=GroupParticipantChoices.ACTIVE
            ).all()
        ]
        ThreadRead.objects.bulk_create(bulk_data)

        instance.is_read = instance.threadread_set.get(user=user).is_read
        return instance
