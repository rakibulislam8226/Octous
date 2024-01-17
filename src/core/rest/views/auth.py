from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..serializers.auth import (
    OTPVerificationSerializer,
    AccountCreationSerializer,
    PhoneNumberSerializer,
)

from ...models import PhoneNumberVerification


class RegisterPhoneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "OTP sent successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            PhoneNumberVerification.objects.update_or_create(
                phone=phone,
                defaults={"verified": True, "verification_time": timezone.now()},
            )
            return Response(
                {
                    "message": "OTP verified successfully. You should create your account within 5 minutes."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AccountCreationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            verification = PhoneNumberVerification.objects.filter(phone=phone).first()

            if not verification or not verification.verified:
                return Response(
                    {"error": "Phone number is not verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the verification is still valid.
            if timezone.now() > verification.verification_time + timedelta(minutes=5):
                return Response(
                    {"error": "Verification has expired. Please verify again."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            return Response(
                {"message": "Account created successfully", "phone": phone},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
