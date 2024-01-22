from channels.generic.websocket import (
    AsyncWebsocketConsumer,
)
from rest_framework.exceptions import NotFound

from threadio.models import ChatGroup


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print(self.scope["user"])
            if not self.scope["user"].is_authenticated:
                raise NotFound("No user authenticated user found.")

            print("Connected to ChatConsumer")

            group: ChatGroup = await ChatGroup.objects.prefetch_related(
                "chatgroupparticipant_set"
            ).aget(uid=self.scope["url_route"]["kwargs"]["group_uid"])
            self.group_name = "chat" + str(group.uid)

            await self.channel_layer.group_add(self.group_name, self.channel_name)

            if not await group.chatgroupparticipant_set.filter(
                user=self.scope["user"]
            ).aexists():
                raise NotFound("No active participant found.")

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
                "message": text_data["message"],
                "room_id": self.group_name,
            },
        )

    async def chat_message(self, event):
        print("asdf ", event, type(event))
        await self.send(event["message"])

    async def disconnect(self, close_code):
        print("disconnected")
