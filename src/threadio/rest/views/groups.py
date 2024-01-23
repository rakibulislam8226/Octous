from django.db.models import Prefetch
from rest_framework import status

from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from threadio.choices import GroupChoices
from threadio.models import ChatGroup, Thread
from threadio.rest.serializers.groups import (
    GroupListSerializer,
    PrivateThreadListSerializer,
)


class PrivateGroupList(ListCreateAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]
    queryset = ChatGroup.objects.filter(status=GroupChoices.ACTIVE)
    parser_classes = [FormParser, MultiPartParser]


class PrivateGroupChatList(ListCreateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]
    serializer_class = PrivateThreadListSerializer

    def get_queryset(self):
        try:
            group = ChatGroup.objects.prefetch_related(
                Prefetch(
                    "thread_set",
                    queryset=Thread.objects.prefetch_related(
                        "replies__replies__replies__replies"
                    )
                    .filter(parent__isnull=True)
                    .all(),
                ),
            ).get(uid=self.kwargs.get("chat_group_uid"), status=GroupChoices.ACTIVE)
        except ChatGroup.DoesNotExist:
            raise NotFound("Group not found")

        return group.thread_set.all()

    def create(self, request, *args, **kwargs):
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        response = super().create(request, *args, **kwargs)

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "chat" + str(self.kwargs.get("chat_group_uid")),
            {
                "type": "chat.message",
                "data": response.data,
                "room_id": str(self.kwargs.get("chat_group_uid")),
            },
        )
        return Response(data=response.data, status=status.HTTP_201_CREATED)
