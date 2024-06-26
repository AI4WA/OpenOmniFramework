from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import (
    completed_emotion_detection,
    completed_quantization_llm,
    completed_speech2text,
    completed_task,
    completed_text2speech,
)

logger = get_logger(__name__)


@receiver(completed_task)
def trigger_completed_task(sender, **kwargs):
    """
    Trigger the multi-modal emotion detection.
    """
    data = kwargs.get("data", {})
    logger.info(data)
    task_data = TaskData(**data)

    if task_data.task_name == "speech2text":
        completed_speech2text.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "emotion_detection":
        completed_emotion_detection.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "quantization_llm":
        completed_quantization_llm.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "text2speech":
        logger.info("Text2Speech task completed")
        completed_text2speech.send(
            sender=sender, data=data, track_id=task_data.track_id
        )
