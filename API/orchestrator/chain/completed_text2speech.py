from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import DataText, Text2Speech
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_text2speech
from orchestrator.models import Task

logger = get_logger(__name__)


@receiver(completed_text2speech)
def trigger_completed_text2speech(sender, **kwargs):
    """
    After the text2speech is done, save it to the database

    Args:
        sender: The sender of the signal
        kwargs: The data passed to the signal
    """
    logger.info("Text2Speech completed triggerred")
    try:
        data = kwargs.get("data", {})
        track_id = kwargs.get("track_id", None)
        logger.info(data)
        task_data = TaskData(**data)

        if track_id is None:
            logger.error("No track_id found")
            return
        # get the speech2text task based on the track_id
        speech2text_task = (
            Task.objects.filter(track_id=track_id, task_name="speech2text")
            .order_by("-created_at")
            .first()
        )
        if speech2text_task is None:
            logger.error("No speech2text task found")
            return
        text = speech2text_task.result_json["result_profile"].get("text", "")
        logger.info(speech2text_task.parameters)
        home_id = speech2text_task.parameters["home_id"]
        text2speech_file = task_data.result_json["result_profile"].get(
            "audio_file_path", ""
        )
        Text2Speech.objects.create(
            home_id=home_id, text=text, text2speech_file=text2speech_file
        )
    except Exception as e:
        logger.exception(e)
        return
