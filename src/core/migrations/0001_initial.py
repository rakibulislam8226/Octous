# Generated by Django 5.0.1 on 2024-01-21 11:58

import autoslug.fields
import core.utils
import dirtyfields.dirtyfields
import django.contrib.auth.validators
import django.utils.timezone
import phonenumber_field.modelfields
import uuid
import versatileimagefield.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhoneNumberVerification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone", models.CharField(max_length=15, unique=True)),
                ("verified", models.BooleanField(default=False)),
                ("verification_time", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        db_index=True,
                        max_length=128,
                        region=None,
                        unique=True,
                        verbose_name="Phone Number",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        editable=False,
                        populate_from=core.utils.get_user_slug,
                        unique=True,
                    ),
                ),
                (
                    "image",
                    versatileimagefield.fields.VersatileImageField(
                        blank=True,
                        upload_to=core.utils.get_user_media_path_prefix,
                        verbose_name="Image",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("PLACEHOLDER", "Placeholder"),
                            ("ACTIVE", "Active"),
                            ("HIDDEN", "Hidden"),
                            ("PAUSED", "Paused"),
                            ("REMOVED", "Removed"),
                        ],
                        db_index=True,
                        default="ACTIVE",
                        max_length=20,
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("FEMALE", "Female"),
                            ("MALE", "Male"),
                            ("UNKNOWN", "Unknown"),
                            ("OTHER", "Other"),
                        ],
                        default="UNKNOWN",
                        max_length=20,
                    ),
                ),
                ("is_online", models.BooleanField(default=False)),
                ("special_pin", models.CharField(blank=True, max_length=6)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("height", models.FloatField(blank=True, null=True)),
                ("weight", models.IntegerField(blank=True, null=True)),
                (
                    "blood_group",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("NOT_SET", "Not Set"),
                            ("A+", "A Positive"),
                            ("A-", "A Negative"),
                            ("B+", "B Positive"),
                            ("B-", "B Negative"),
                            ("AB+", "Ab Positive"),
                            ("AB-", "Ab Negative"),
                            ("O+", "O Positive"),
                            ("O-", "O Negative"),
                        ],
                        default="NOT_SET",
                        max_length=10,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ("-date_joined",),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
    ]
