import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from threadio.choices import GroupParticipantChoices
from threadio.models import ChatGroup, ChatGroupParticipant


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
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


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
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


# consumers.py


class GroupVoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        # Join the group's signaling channel
        group_uid = self.scope["url_route"]["kwargs"]["group_uid"]
        self.group_name = f"group_call_{group_uid}"

        # Check if the user has permission to join the group call
        if not await self.has_permission():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group's signaling channel
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def has_permission(self):
        # Check if the user has permission to join the group call
        user_id = self.scope["user"].id
        group_uid = self.scope["url_route"]["kwargs"]["group_uid"]

        try:
            ChatGroupParticipant.objects.get(
                user_id=user_id,
                group__uid=group_uid,
                status=GroupParticipantChoices.ACTIVE,  # Adjust this based on your participant status logic
            )
            return True
        except ChatGroupParticipant.DoesNotExist:
            return False

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data["type"]

        if message_type == "offer":
            # Handle WebRTC offer and send it to the group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "webrtc.offer",
                    "offer": data["offer"],
                    "user_uid": self.scope["user"].uid,
                },
            )
        elif message_type == "answer":
            # Handle WebRTC answer and send it to the group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "webrtc.answer",
                    "answer": data["answer"],
                    "user_uid": self.scope["user"].uid,
                },
            )
        elif message_type == "ice_candidate":
            # Handle ICE candidate and send it to the group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "webrtc.ice_candidate",
                    "ice_candidate": data["ice_candidate"],
                    "user_uid": self.scope["user"].uid,
                },
            )

    async def webrtc_offer(self, event):
        # Broadcast WebRTC offer to the group
        await self.send(
            text_data=json.dumps(
                {
                    "type": "webrtc.offer",
                    "offer": event["offer"],
                    "user_uid": event["user_uid"],
                }
            )
        )

    async def webrtc_answer(self, event):
        # Broadcast WebRTC answer to the group
        await self.send(
            text_data=json.dumps(
                {
                    "type": "webrtc.answer",
                    "answer": event["answer"],
                    "user_id": event["user_uid"],
                }
            )
        )

    async def webrtc_ice_candidate(self, event):
        # Broadcast ICE candidate to the group
        await self.send(
            text_data=json.dumps(
                {
                    "type": "webrtc.ice_candidate",
                    "ice_candidate": event["ice_candidate"],
                    "user_uid": event["user_uid"],
                }
            )
        )
