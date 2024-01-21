from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from threadio.choices import GroupChoices
from threadio.models import ChatGroup, Thread
from threadio.rest.serializers.groups import GroupListSerializer


class PrivateGroupList(ListCreateAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]
    queryset = ChatGroup.objects.filter(status=GroupChoices.ACTIVE)
    parser_classes = [FormParser, MultiPartParser]


class PrivateGroupChatList(ListCreateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            group = ChatGroup.objects.prefetch_related(
                "thread_set__threadread_set"
            ).get(uid=self.kwargs.get("uid"))
        except ChatGroup.DoesNotExist:
            raise NotFound("Group not found")
        return group.threadread_set.all()
