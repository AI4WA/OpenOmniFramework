from django.db.models.signals import post_save
from django.dispatch import receiver

from hardware.models import DataAudio, DataMultiModalConversation


@receiver(post_save, sender=DataAudio)
def add_data_multimodal_conversation_entry(sender, instance, created, **kwargs):
    """
    Add data multimodal conversation
    """
    if created:
        DataMultiModalConversation.objects.create(
            audio=instance, track_id=instance.track_id
        )
