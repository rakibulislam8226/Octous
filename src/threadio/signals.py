from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from threadio.choices import GroupParticipantChoices
from threadio.models import Thread, ThreadRead, GroupParticipant


@receiver(pre_save, sender=Thread)
def create_thread_users_after_sending_thread(
    sender, instance: Thread, created, **kwargs
):
    if created:
        ThreadRead.objects.bulk_create(
            [
                ThreadRead(thread=instance, user=group_participant.user)
                for group_participant in GroupParticipant.objects.filter(
                    group=instance.group
                ).all()
                if group_participant.status == GroupParticipantChoices.ACTIVE
            ]
        )
