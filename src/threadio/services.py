from threadio.models import ChatGroup


class ThreadService:
    def create_group(self, group_name) -> ChatGroup:
        group, _ = ChatGroup.objects.get_or_create(name=group_name)
        return group
