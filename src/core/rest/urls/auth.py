from django.urls import path

from ..views.auth import RegisterPhoneView, VerifyOTPView, CompleteAccountView

urlpatterns = [
    path("", RegisterPhoneView.as_view(), name="core.register"),
    path("/verify-otp", VerifyOTPView.as_view(), name="core.verify-otp"),
    path("/create-account", CompleteAccountView.as_view(), name="core.create-account"),
]
