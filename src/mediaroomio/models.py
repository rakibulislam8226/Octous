from django.contrib.auth import get_user_model
from django.db import models

from versatileimagefield.fields import PPOIField

from common.models import BaseModelWithUID

from versatileimagefield.fields import VersatileImageField


User = get_user_model()


# Create your models here.
class MediaRoom(BaseModelWithUID):
    # image
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    # General Information
    file = models.FileField(null=True, blank=True)


class MediaRoomConnector(BaseModelWithUID):
    # Relationship Important
    media_room = models.ForeignKey("mediaroomio.MediaRoom", on_delete=models.CASCADE)

    # Relationship ForeignKey
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
