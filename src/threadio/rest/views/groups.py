from django.db.models import Prefetch, Case, When, Value, BooleanField
from django.utils import timezone
from rest_framework import status

from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.rest.serializers.users import UserMinReadOnlySerializer
from threadio.choices import GroupChoices
from threadio.models import ChatGroup, Thread, ThreadRead
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
        user = self.request.user
        try:
            group = ChatGroup.objects.prefetch_related(
                Prefetch(
                    "thread_set",
                    queryset=Thread.objects.prefetch_related(
                        "replies__replies__replies__replies",
                        Prefetch(
                            "threadread_set",
                            queryset=ThreadRead.objects.select_related("user"),
                            to_attr="read_users",
                        ),
                    )
                    .filter(parent__isnull=True)
                    .distinct()
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
        print("sfasf ", response.data)

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


class PrivateGroupThreadReadNowList(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        group_uid = self.kwargs.get("chat_group_uid")
        user = self.request.user
        try:
            chat_group = ChatGroup.objects.prefetch_related(
                "chatgroupparticipant_set", "threadread_set"
            ).get(uid=group_uid)
        except ChatGroup.DoesNotExist:
            raise NotFound(detail="Group not found")
        # chat last seen
        print("last seend ", chat_group.chatgroupparticipant_set.filter(user=user))
        chat_group.chatgroupparticipant_set.filter(user=user).update(
            last_seen=timezone.now()
        )

        # read all messages
        print(
            "read all chat , ",
            chat_group.id,
            chat_group.threadread_set.filter(),
        )
        chat_user_threads = chat_group.threadread_set.filter(user=user, is_read=False)
        if chat_user_threads.exists():
            chat_user_threads.update(is_read=True)

            user_serialized_data = UserMinReadOnlySerializer(
                user, context={"request": self.request}
            ).data

            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                "last_seen_user" + str(self.kwargs.get("chat_group_uid")),
                {
                    "type": "chat.message",
                    "data": user_serialized_data,
                    "room_id": str(self.kwargs.get("chat_group_uid")),
                },
            )
        return Response(status=status.HTTP_200_OK, data="All message has seen.")
