from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import speech2text_completed, task_completed

logger = get_logger(__name__)


@receiver(task_completed)
def trigger_task_finished(sender, **kwargs):
    """
    Trigger the multi-modal emotion detection.
    """
    data = kwargs.get("data", {})
    logger.info(data)
    task_data = TaskData(**data)

    if task_data.task_name == "speech2text":
        speech2text_completed.send(sender=sender, data=data)
