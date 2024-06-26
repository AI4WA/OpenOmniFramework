from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import DataAudio, DataText
from orchestrator.chain.cluster import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_speech2text, created_data_text

logger = get_logger(__name__)


@receiver(completed_speech2text)
def trigger_completed_speech2text(sender, **kwargs):
    """
    After the speech2text is done, save it to the database

    Args:
        sender: The sender of the signal
        kwargs: The data passed to the signal
    """
    logger.info("Speech2Text completed triggerred")
    data = kwargs.get("data", {})
    track_id = kwargs.get("track_id", None)
    task_data = TaskData(**data)
    params = task_data.parameters
    logger.info(track_id)

    uid = params.get("uid")
    home_id = params.get("home_id")
    audio_index = params.get("audio_index")

    audio = DataAudio.objects.filter(
        home_id=home_id, uid=uid, sequence_index=audio_index
    )
    logger.debug(audio)
    if not audio:
        logger.error("Audio not found")
        return
    if len(audio) > 1:
        logger.error("Multiple audio found")
        return
    audio_obj = audio.first()

    # save the data to the database
    result_json = task_data.result_json
    result_profile = result_json.get("result_profile", {})
    text = result_profile.get("text", "")
    logger.debug(result_json)
    data_text_obj = DataText.objects.filter(audio=audio_obj, home_id=home_id).first()
    if data_text_obj:
        data_text_obj.text = text
        data_text_obj.save()
    else:
        data_text_obj = DataText(
            home_id=home_id,
            audio=audio_obj,
            text=text,
        )
        data_text_obj.save()

    ClusterManager.chain_next(
        track_id=track_id,
        current_component="completed_speech2text",
        next_component_params={"sender": data_text_obj, "data": data_text_obj.__dict__},
    )
