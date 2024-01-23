from django.urls import path

from ..views import groups

urlpatterns = [
    path(
        "/<uuid:chat_group_uid>/threads",
        groups.PrivateGroupChatList.as_view(),
        name="group-chat-list",
    ),
    path(
        "/<uuid:chat_group_uid>/threads/read-now",
        groups.PrivateGroupThreadReadNowList.as_view(),
        name="group-thread-read-now",
    ),
    path("", groups.PrivateGroupList.as_view(), name="group-list"),
]
