from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        "ws/chat/<uuid:group_uid>",
        consumers.ChatConsumer.as_asgi(),
    )
]
