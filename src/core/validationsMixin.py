from django.utils import timezone

from rest_framework.serializers import ValidationError


class UserCommonValidationMixin:
    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError({"Password error": "Passoword do no match."})

        return attrs
