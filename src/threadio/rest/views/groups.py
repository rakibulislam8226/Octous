from django.db.models import Prefetch
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

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
