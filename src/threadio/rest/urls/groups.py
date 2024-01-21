from django.urls import path
from ..views import groups

urlpatterns = [
    path(
        "/<uuid:uid>/chats",
        groups.PrivateGroupChatList.as_view(),
        name="group-chat-list",
    ),
    path("", groups.PrivateGroupList.as_view(), name="group-list"),
]
