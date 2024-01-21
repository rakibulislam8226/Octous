from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from threadio.choices import GroupChoices
from threadio.models import Group
from threadio.rest.serializers.groups import GroupListSerializer


class PrivateGroupList(ListCreateAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.filter(status=GroupChoices.ACTIVE)
