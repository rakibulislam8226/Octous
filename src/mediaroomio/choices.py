from django.db import models


class MediaKindChoices(models.TextChoices):
    VIDEO_RESUME = "VIDEO_RESUME", "Video Resume"
    IMAGE = "IMAGE", "Image"
    VIDEO = "VIDEO", "Video"
    ASSESSMENT = "ASSESSMENT", "Assessment"
