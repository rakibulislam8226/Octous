from django.urls import path, include

urlpatterns = [
    path("/auth", include("core.rest.urls.auth")),
]
