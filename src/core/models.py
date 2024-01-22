from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from versatileimagefield.fields import VersatileImageField

from common.models import BaseModelWithUID

from .choices import UserStatus, UserGender, BloodGroups
from .managers import CustomUserManager
from .utils import get_user_slug, get_user_media_path_prefix


class User(AbstractUser, BaseModelWithUID, PermissionsMixin):
    phone = PhoneNumberField(unique=True, db_index=True, verbose_name="Phone Number")
    name = models.CharField(max_length=255, blank=True)
    slug = AutoSlugField(populate_from=get_user_slug, unique=True)
    image = VersatileImageField(
        "Image",
        upload_to=get_user_media_path_prefix,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        db_index=True,
        default=UserStatus.ACTIVE,
    )
    gender = models.CharField(
        max_length=20,
        blank=True,
        choices=UserGender.choices,
        default=UserGender.UNKNOWN,
    )
    is_online = models.BooleanField(default=False)
    special_pin = models.CharField(max_length=6, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    blood_group = models.CharField(
        max_length=10,
        blank=True,
        choices=BloodGroups.choices,
        default=BloodGroups.NOT_SET,
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return f"UID: {self.uid}, Phone: {self.phone}"

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.username = self.phone
        super().save(*args, **kwargs)


class PhoneNumberVerification(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone}, verified: {self.verified}"
