from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint, Q

from autoslug import AutoSlugField
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.serializers import VersatileImageFieldSerializer

from common.models import BaseModelWithUID
from common.variable import versatile_image_size
from threadio.choices import (
    GroupChoices,
    GroupParticipantChoices,
    GroupParticipantRoleChoices,
)

User = get_user_model()


class ChatGroup(BaseModelWithUID):
    name = models.CharField(max_length=220, blank=True)
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        max_length=255,
    )
    description = models.TextField(blank=True)
    banner = models.ForeignKey(
        "mediaroomio.MediaRoom", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=GroupChoices.choices,
        default=GroupChoices.ACTIVE,
        db_index=True,
    )
    is_need_approval = models.BooleanField(default=False)
    disable_till = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If group is ban, admin should give time when it will active again.",
    )
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(
        User, through="threadio.ChatGroupParticipant", related_name="chat_groups"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name"],
                condition=~Q(name=""),
                name="group_name_must_be_uniuqe",
                violation_error_message="Group name must be unique.",
            )
        ]


class ChatGroupParticipant(BaseModelWithUID):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=GroupParticipantChoices.choices,
        default=GroupParticipantChoices.PENDING,
        db_index=True,
    )
    role = models.TextField(
        max_length=20,
        choices=GroupParticipantRoleChoices.choices,
        default=GroupParticipantRoleChoices.PUBLIC,
    )
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("group", "user")


class Thread(BaseModelWithUID):
    content = models.TextField(blank=True)
    media_room = models.ForeignKey(
        "mediaroomio.MediaRoom", on_delete=models.PROTECT, null=True, blank=True
    )

    # FK
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="messages_sender"
    )
    group = models.ForeignKey(ChatGroup, on_delete=models.PROTECT, db_index=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="replies",
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

    # signal will create ThreadRead automatically for user


class ThreadRead(BaseModelWithUID):
    thread = models.ForeignKey(Thread, on_delete=models.PROTECT, db_index=True)
    group = models.ForeignKey(
        ChatGroup, on_delete=models.PROTECT, blank=True, null=True
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    is_read = models.BooleanField(default=False, db_index=True)
