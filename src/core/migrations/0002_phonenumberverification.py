# Generated by Django 4.2.4 on 2024-01-17 08:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
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
    ]