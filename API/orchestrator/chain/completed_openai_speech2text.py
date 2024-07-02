from datetime import timedelta

from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import DataAudio, DataVideo
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

    start_time = audio_obj.start_time
    end_time = audio_obj.end_time

    # get the video data based on the audio data time range
    start_time = start_time.replace(second=0, microsecond=0)
    end_time = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    logger.info(f"Start time: {start_time}, End time: {end_time}")

    video_data = DataVideo.objects.filter(
        video_record_minute__range=[start_time, end_time]
    )
    logger.info(video_data)

    images_path = []
    for video in video_data:
        image_folder_name = video.video_file.split(".")[0].rsplit("-", 1)[0]
        images_path.append(f"{video.uid}/frames/{image_folder_name}")

    images_path_list = []
    for image_path in images_path:
        folder = f"videos/{image_path}"
        images_path_list.append(folder)

    logger.info(f"Text: {text}, Images: {len(images_path_list)}")

    task_params = {
        "text": text,
        "images_path_list": images_path_list,
    }
    ClusterManager.chain_next(
        track_id=track_id,
        current_component="completed_openai_speech2text",
        next_component_params=task_params,
        user=sender.user,
    )
