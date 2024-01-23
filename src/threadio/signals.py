from asgiref.sync import async_to_sync
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from threadio.choices import GroupParticipantChoices
from threadio.models import Thread, ThreadRead, ChatGroupParticipant


@receiver(post_save, sender=Thread)
def create_thread_users_after_sending_thread(sender, instance, created, **kwargs):
    if created:
        ThreadRead.objects.bulk_create(
            [
                ThreadRead(thread=instance, user=group_participant.user)
                for group_participant in ChatGroupParticipant.objects.filter(
                    group=instance.group
                ).all()
                if group_participant.status == GroupParticipantChoices.ACTIVE
            ]
        )


# @receiver(post_save, sender=Thread)
# def send_thread_message_to_channel_group(sender, instance: Thread, **kwargs):
#     from channels.layers import get_channel_layer
#
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "chat" + str(instance.group.uid),
#         {
#             "type": "chat.message",
#             "message": instance,
#             "room_id": str(instance.group.uid),
#         },
#     )
#
#     print(channel_layer)


@receiver(post_save, sender=ThreadRead)
def send_thread_message_to_channel_group(
    sender, instance: ThreadRead, created, **kwargs
):
    if created:
        if instance.group is None or not instance.group:
            instance.group = instance.thread.group
            instance.save_dirty_fields()
