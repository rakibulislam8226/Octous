import random
from typing import Dict

from django.core.cache import cache

from rest_framework_simplejwt.tokens import RefreshToken

from twilio.rest import Client


def get_user_slug(instance):
    return f"{instance.username}--{str(instance.uid).split('-')[0]}"


# Media File Prefixes
def get_user_media_path_prefix(instance, filename):
    return f"Media/users/{instance.slug}/{filename}"


# Generate Token Manually
def get_tokens_for_user(user) -> Dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def generate_otp():
    return str(random.randint(1000, 9999))


def store_otp(phone, otp):
    cache.set(phone, otp, timeout=300)  # OTP valid for 5 minutes


def verify_otp(phone, otp):
    cached_otp = cache.get(phone)
    return cached_otp == otp


# NOTE: This is the configure for twilio setting for otp sending
# def send_otp_via_sms(phone_number, otp):
#     account_sid = "YOUR_TWILIO_ACCOUNT_SID"
#     auth_token = "YOUR_TWILIO_AUTH_TOKEN"
#     client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         body=f"Your OTP is: {otp}", from_="YOUR_TWILIO_PHONE_NUMBER", to=phone_number
#     )
#     return message.sid


# For developemet purpose only
def send_otp_via_sms(phone_number, otp):
    print(f"OTP for {phone_number} is {otp}")
