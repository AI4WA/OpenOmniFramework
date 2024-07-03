from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import DataAudio, DataMultiModalConversation, DataText
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_openai_speech2text

logger = get_logger(__name__)


@receiver(completed_openai_speech2text)
def trigger_completed_openai_speech2text(sender, **kwargs):
    """
    We will need to gather the text, and then grab the video to the next step

    Args:
        sender: The sender of the signal
        **kwargs: The data passed to the signal

    Returns:

    """
    logger.info("OpenAI Speech2Text completed triggerred")
    data = kwargs.get("data", {})
    track_id = kwargs.get("track_id", None)
    task_data = TaskData(**data)
    params = task_data.parameters
    logger.info(track_id)

    # get the text
    result_json = task_data.result_json
    result_profile = result_json.get("result_profile", {})
    text = result_profile.get("text", "")
    logger.info(text)

    # Currently GPT-4o can only take images, so we will try to locate the relevant images
    uid = params.get("uid")
    home_id = params.get("home_id")
    audio_index = params.get("audio_index")

    audio = DataAudio.objects.filter(
        home_id=home_id, uid=uid, sequence_index=audio_index
    )

    if not audio:
        logger.error("Audio not found")
        return
    if len(audio) > 1:
        logger.error("Multiple audio found")
        return
    audio_obj = audio.first()

    data_text_obj = DataText.objects.filter(audio=audio_obj).first()
    if data_text_obj:
        data_text_obj.text = text
        data_text_obj.save()
    else:
        data_text_obj = DataText(
            audio=audio_obj,
            text=text,
        )
        data_text_obj.save()

    if not hasattr(audio_obj, "multi_modal_conversation"):
        DataMultiModalConversation.objects.create(
            audio=audio_obj,
        )
    audio_obj.multi_modal_conversation.text = data_text_obj
    audio_obj.multi_modal_conversation.save()

    ClusterManager.chain_next(
        track_id=track_id,
        current_component="completed_openai_speech2text",
        next_component_params={"sender": data_text_obj, "data": data_text_obj.__dict__},
        user=sender.user,
    )
