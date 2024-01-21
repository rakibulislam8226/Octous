from django.urls import path
from ..views import groups

urlpatterns = [
    path("/<uuid:uid>", groups.PrivateGroupList.as_view(), name="group-list"),
    path("", groups.PrivateGroupList.as_view(), name="group-list"),
]
