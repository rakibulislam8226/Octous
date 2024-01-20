from autoslug import AutoSlugField
from django.db import models
from django.contrib.auth import get_user_model

from common.models import BaseModelWithUID
from threadio.choices import (
    GroupChoices,
    GroupParticipantChoices,
    GroupParticipantRoleChoices,
)

User = get_user_model()


class Group(BaseModelWithUID):
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
        max_length=20, choices=GroupChoices.choices, default=GroupChoices.ACTIVE
    )
    is_need_approval = models.BooleanField(default=False)
    disable_till = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If group is ban, admin should give time when it will active again.",
    )


class GroupParticipant(BaseModelWithUID):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    status = models.CharField(
        max_length=20,
        choices=GroupParticipantChoices.choices,
        default=GroupParticipantChoices.PENDING,
    )
    role = models.TextField(
        max_length=20,
        choices=GroupParticipantRoleChoices.choices,
        default=GroupParticipantRoleChoices.PUBLIC,
    )
    last_seen = models.DateTimeField(null=True, blank=True)


class Thread(BaseModelWithUID):
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="messages/", blank=True, null=True)

    # FK
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="messages_sender"
    )
    group = models.ForeignKey(Group, on_delete=models.PROTECT)

    # signal will create ThreadRead automatically for user


class ThreadRead(BaseModelWithUID):
    thread = models.ForeignKey(Thread, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    is_read = models.BooleanField(default=False)
