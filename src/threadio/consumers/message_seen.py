import ast
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from threadio.models import ChatGroup


class ChatLastMessageSeenByConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            if not self.scope["user"].is_authenticated:
                await self.close()

            group: ChatGroup = await ChatGroup.objects.prefetch_related(
                "chatgroupparticipant_set",
            ).aget(uid=self.scope["url_route"]["kwargs"]["group_uid"])
            self.group_name = "last_seen_user" + str(group.uid)

            await self.channel_layer.group_add(self.group_name, self.channel_name)

        except Exception as e:
            print(e)
            await self.close()

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
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
        await self.send(json.dumps(event["data"]))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
