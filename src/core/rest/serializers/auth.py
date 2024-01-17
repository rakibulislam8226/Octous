from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from ...models import User
from ...utils import verify_otp, generate_otp, send_otp_via_sms, store_otp


class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def create(self, validated_data):
        phone = validated_data.get("phone")
        otp = generate_otp()
        send_otp_via_sms(phone, otp)
        store_otp(phone, otp)
        return validated_data


class OTPVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        phone = data.get("phone")
        otp = data.get("otp")

        if not verify_otp(phone, otp):
            raise serializers.ValidationError("Invalid OTP")

        return data


class AccountCreationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15, write_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "phone",
            "email",
            "password",
            "confirm_password",
        )

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise ValidationError("A user with this phone number already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields didn't match."}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create(
            phone=validated_data["phone"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
