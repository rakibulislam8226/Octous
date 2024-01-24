import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from threadio.choices import GroupParticipantChoices
from threadio.models import ChatGroupParticipant


class GroupVoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        # Join the group's signaling channel
        group_uid = self.scope["url_route"]["kwargs"]["group_uid"]
        self.group_name = f"group_call_{group_uid}"

        if not await self.has_permission():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Leave the group's signaling channel."""

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def has_permission(self):
        """Check if the user has permission to join the group call."""

        user_id = self.scope["user"].id
        group_uid = self.scope["url_route"]["kwargs"]["group_uid"]

        try:
            ChatGroupParticipant.objects.get(
                user_id=user_id,
                group__uid=group_uid,
                status=GroupParticipantChoices.ACTIVE,
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
        """Broadcast WebRTC offer to the group."""

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
        """Broadcast WebRTC answer to the group."""

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
        """Broadcast ICE candidate to the group."""
        
        await self.send(
            text_data=json.dumps(
                {
                    "type": "webrtc.ice_candidate",
                    "ice_candidate": event["ice_candidate"],
                    "user_uid": event["user_uid"],
                }
            )
        )
