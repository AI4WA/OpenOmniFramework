from datetime import timedelta

from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import DataText, DataVideo
from orchestrator.chain.signals import data_text_created
from orchestrator.models import Task

logger = get_logger("Emotion-Detection-Chain")


@receiver(data_text_created)
def trigger_multi_modal_emotion_detection(sender, **kwargs):
    """
    This function will trigger the emotion detection model with the latest data

    It will first look for the latest data_text,
    and then get the audio and image data based on the time range of the audio data

    Args:
        sender: The sender of the signal
        kwargs: The data passed to the signal
    Returns:

    """
    data = kwargs.get("data", {})
    data_text_id = data.get("id", None)
    # get the audio data, which have not been process and have the text information
    if data_text_id:
        data_text = DataText.objects.get(id=data_text_id)
    else:
        data_text = (
            DataText.objects.filter(pipeline_triggered=False)
            .order_by("-created_at")
            .first()
        )
    if data_text is None:
        logger.info("No text to act on found")
        return None, None, None, None
    text = data_text.text

    data_audio = data_text.audio

    audio_file = f"audio/{data_audio.uid}/{data_audio.audio_file}"

    # get the image data based on the audio data time range
    # TODO: this will be changed rapidly
    start_time = data_audio.start_time
    end_time = data_audio.end_time
    # round the start to the minute level down
    start_time = start_time.replace(second=0, microsecond=0)
    # round the end to the minute level up
    end_time = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    logger.info(f"Start time: {start_time}, End time: {end_time}")
    logger.info(data_audio)
    # we will assume it comes from the same device
    # list all videos has overlap with [start_time, end_time]
    videos_data = DataVideo.objects.filter(
        video_record_minute__range=[start_time, end_time]
    )

    images_path = []
    for video_data in videos_data:
        image_folder_name = video_data.video_file.split(".")[0].rsplit("-", 1)[0]
        images_path.append(f"{video_data.uid}/frames/{image_folder_name}")

    # I need to read image files into List[np.ndarray]
    images_path_list = []
    for image_path in images_path:
        # loop the path, get all images
        folder = f"videos/{image_path}"
        images_path_list.append(folder)

    # trigger the model
    logger.info(f"Text: {text}, Audio: {audio_file}, Images: {len(images_path_list)}")

    task_params = {
        "text": text,
        "audio_file": audio_file,
        "images_path_list": images_path_list,
        "data_text_id": data_text.id,
    }
    Task.create_task(
        user=None,
        name="Emotion Detection",
        task_name="emotion_detection",
        parameters=task_params,
    )
    return text, [audio_file], images_path_list, data_text
