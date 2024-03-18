import os
from datetime import timedelta

import cv2
from django.conf import settings
from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from hardware.models import AudioData, VideoData
from ml.ml_models.emotion_detection import trigger_model

logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Run the worker to finish the llm or stt tasks.'

    def handle(self, *args, **options):
        """
        Grab all the images/text/audio from the database and run the emotion detection model on them

        """

        # get the audio data
        audio_data = AudioData.objects.all().order_by("-created_at").first()
        if audio_data is None:
            logger.info("No audio data found")
            return
        text = audio_data.text

        audio_file = (settings.CLIENT_DATA_FOLDER / "Listener" / "data" / "audio" / audio_data.uid
                      / "audio" / audio_data.audio_file).as_posix()

        # get the image data based on the audio data time range
        # TODO: this will be changed rapidly
        start_time = audio_data.start_time
        end_time = audio_data.end_time
        # round the start to the minute level down
        start_time = start_time.replace(second=0, microsecond=0)
        # round the end to the minute level up
        end_time = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        logger.info(f"Start time: {start_time}, End time: {end_time}")
        logger.info(audio_data)
        # we will assume it comes from the same device
        # list all videos has overlap with [start_time, end_time]
        videos_data = VideoData.objects.filter(
            video_record_minute__range=[start_time, end_time]
        )

        images_path = []
        for video_data in videos_data:
            image_folder_name = video_data.video_file.split(".")[0].rsplit("-", 1)[0]
            images_path.append(f"{video_data.uid}/frames/{image_folder_name}")

        # I need to read image files into List[np.ndarray]
        image_np_list = []
        for image_path in images_path:
            # loop the path, get all images
            folder = settings.CLIENT_DATA_FOLDER / "Listener" / "data" / "videos" / image_path

            if not folder.exists():
                continue
            for image_file in os.listdir(folder):
                image = cv2.imread((folder / image_file).as_posix())
                image_np_list.append(image)

        # trigger the model
        logger.info(f"Text: {text}, Audio: {audio_file}, Images: {len(image_np_list)}")
        trigger_model(text, [audio_file], image_np_list)
