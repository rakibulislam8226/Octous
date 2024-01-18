from django.db import models
from django.contrib.auth import get_user_model

from common.models import BaseModelWithUID

User = get_user_model


class Message(BaseModelWithUID):
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="messages/", blank=True)
    is_read = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # FK
    sender = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="messages_sender"
    )
    receipient = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages_receipient",
    )
    # Group is not created yet.

    def __str__(self) -> str:
        return f"{self.sender} to {self.receipient if self.receipient else 'Group'}"
