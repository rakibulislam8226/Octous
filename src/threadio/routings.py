from django.urls import path

from .consumers.chat import ChatConsumer
from .consumers.message_seen import ChatLastMessageSeenByConsumer
from .consumers.voice_call import GroupVoiceConsumer

websocket_urlpatterns = [
    path(
        "ws/chat/<uuid:group_uid>",
        ChatConsumer.as_asgi(),
    ),
    path(
        "ws/chat/<uuid:group_uid>/last-message-seen-by",
        ChatLastMessageSeenByConsumer.as_asgi(),
    ),
    path(
        "ws/call/<uuid:group_uid>",
        GroupVoiceConsumer.as_asgi(),
    ),
]
