from threadio.models import Group


class ThreadService:
    def create_group(self, group_name) -> Group:
        group, _ = Group.objects.get_or_create(name=group_name)
        return group
