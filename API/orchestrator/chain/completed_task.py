from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import (
    completed_emotion_detection,
    completed_hf_llm,
    completed_openai_gpt_4o_text_and_image,
    completed_openai_gpt_4o_text_only,
    completed_openai_speech2text,
    completed_openai_text2speech,
    completed_quantization_llm,
    completed_speech2text,
    completed_task,
    completed_text2speech,
)
from orchestrator.models import Task

logger = get_logger(__name__)


@receiver(completed_task)
def trigger_completed_task(sender, **kwargs):
    """
    Trigger the multi-modal emotion detection.
    """
    data = kwargs.get("data", {})
    task_data = TaskData(**data)

    if task_data.task_name == "speech2text":
        return completed_speech2text.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "emotion_detection":
        return completed_emotion_detection.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "quantization_llm":
        return completed_quantization_llm.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "text2speech":
        logger.info("Text2Speech task completed")
        return completed_text2speech.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "hf_llm":
        logger.info("HF LLM task completed")
        return completed_hf_llm.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "openai_speech2text":
        logger.info("OpenAI Speech2Text task completed")
        return completed_openai_speech2text.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "openai_gpt_4o_text_and_image":
        logger.info("OpenAI GPT4O task completed")
        return completed_openai_gpt_4o_text_and_image.send(
            sender=sender, data=data, track_id=task_data.track_id
        )
    if task_data.task_name == "openai_gpt_4o_text_only":
        logger.info("OpenAI GPT4O Text Only task completed")
        return completed_openai_gpt_4o_text_only.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    if task_data.task_name == "openai_text2speech":
        logger.info("OpenAI Text2Speech task completed")
        return completed_openai_text2speech.send(
            sender=sender, data=data, track_id=task_data.track_id
        )

    task_name_choices = Task.get_task_name_choices()
    task_name_choices_list = [task[0] for task in task_name_choices]
    if task_data.task_name not in task_name_choices_list:
        logger.error("Task name not found is not in the choices list")
        return
    logger.critical(f"{task_data.task_name} task completed, however, no action taken.")
