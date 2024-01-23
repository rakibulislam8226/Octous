import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
)
from django.db.models import Prefetch
from rest_framework.exceptions import NotFound

from threadio.models import ChatGroup, Thread
from threadio.rest.serializers.groups import PrivateThreadListSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            if not self.scope["user"].is_authenticated:
                await self.close()

            group: ChatGroup = await ChatGroup.objects.prefetch_related(
                "chatgroupparticipant_set",
            ).aget(uid=self.scope["url_route"]["kwargs"]["group_uid"])
            self.group_name = "chat" + str(group.uid)

            await self.channel_layer.group_add(self.group_name, self.channel_name)

            if not await group.chatgroupparticipant_set.filter(
                user=self.scope["user"]
            ).aexists():
                await self.close()

        except Exception as _:
            await self.close()

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        import ast

        text_data = ast.literal_eval(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "data": text_data,
                "room_id": self.group_name,
            },
        )

    async def chat_message(self, event):
        print("asdf ", event, type(event))
        await self.send(json.dumps(event["data"]))

    async def disconnect(self, close_code):
        print("disconnected")
