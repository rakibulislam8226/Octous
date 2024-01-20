from django.db import models


class MediaKindChoices(models.TextChoices):
    IMAGE = "IMAGE", "Image"
    VIDEO = "VIDEO", "Video"
    FILE = "FILE", "File"
