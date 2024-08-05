import os
from datetime import datetime
from typing import List, Optional, Tuple

import cv2
import torch

from models.parameters import EmotionDetectionParameters
from models.task import ResultStatus, Task
from models.track_type import TrackType
from modules.emotion_detection.features_extraction import FeaturesExtractor
from modules.emotion_detection.sentiment import SentimentAnalysis
from utils.constants import CLIENT_DATA_FOLDER, EMOTION_DETECTION_MODEL_DIR
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker

deepface_dir = EMOTION_DETECTION_MODEL_DIR / ".deepface" / "weights"
deepface_dir.mkdir(parents=True, exist_ok=True)
# set the environment variable
os.environ["DEEPFACE_HOME"] = EMOTION_DETECTION_MODEL_DIR.as_posix()

models_dir = EMOTION_DETECTION_MODEL_DIR / "model_data"

logger = get_logger(__name__)


class EmotionDetectionHandler:

    def handle_task(self, task: Task) -> Optional[Task]:
        """
        Handle the task
        Args:
            task (Task): The task to handle
        Returns:
            The task with the result
        """
        emotion_detection_parameters = EmotionDetectionParameters(**task.parameters)
        text = emotion_detection_parameters.text
        audio_file = emotion_detection_parameters.audio_file
        images_path_list = emotion_detection_parameters.images_path_list

        logger.info(f"Text: {text}")
        logger.info(f"Audio: {audio_file}")
        logger.info(f"Images: {len(images_path_list)}")
        TimeLogger.log_task(task, "start_trigger_emotion_model")
        result_profile, latency_profile = self.trigger_model(
            text, [audio_file], images_path_list
        )
        TimeLogger.log_task(task, "end_trigger_emotion_model")
        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        return task

    @staticmethod
    def trigger_model(
        text: str, audio_paths: List[str], images_paths: List[str]
    ) -> Tuple[dict, dict]:
        """

        Args:
            text (str): The text to analyze for emotion
            audio_paths (List[str]): The audio data to analyze for emotion
            images_paths (List[str]): The images data to analyze for emotion

        Returns:

        """
        result_profile = {}
        latency_profile = {}

        if not text or not audio_paths or not images_paths:
            logger.error("No text or audio or images provided")
            logger.error(
                f"text: {text is None}, audio: {audio_paths is None}, images: {images_paths is None}"
            )
            return {}, {}
        # audio is the file path
        # same as the images, we need to read the images first
        audio = []
        for audio_path in audio_paths:
            audio.append((CLIENT_DATA_FOLDER / audio_path).as_posix())

        start_time = datetime.now()
        # read the images
        images = []
        for images_path in images_paths:
            folder = CLIENT_DATA_FOLDER / images_path
            if not folder.exists():
                continue
            # Time Killer
            for image_file in folder.iterdir():
                image = cv2.imread(image_file.as_posix())
                images.append(image)
        latency_profile["io_images_read"] = (
            datetime.now() - start_time
        ).total_seconds()

        # 1. get the features with bert cn model
        with time_tracker(
            "feature_extraction", latency_profile, track_type=TrackType.MODEL.value
        ):
            features_extractor = FeaturesExtractor()
            feature_video = (
                features_extractor.get_images_tensor(images)
                if images is not None
                else None
            )  # (n/5,709)
            feature_audio = (
                features_extractor.get_audio_embedding(audio)
                if audio is not None
                else None
            )  # (94,33)

        (
            logger.info(f"feature_video: {feature_video.shape}")
            if feature_video is not None
            else logger.info("feature_video: there are no information about video")
        )
        (
            logger.info(f"feature_audio: {feature_audio.shape}")
            if feature_audio is not None
            else logger.info("feature_audio: there are no information about audio")
        )

        # data is ready
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = SentimentAnalysis().to(device)
        # load the model
        with time_tracker(
            "load_model", latency_profile, track_type=TrackType.MODEL.value
        ):
            model.load_state_dict(
                {
                    k.replace("Model.", ""): v
                    for k, v in torch.load(models_dir / "sa_sims.pth").items()
                },
                strict=True,
            )

            model.eval()

        # run model
        with time_tracker("infer", latency_profile, track_type=TrackType.MODEL.value):
            output = model(text, feature_audio, feature_video)

        logger.critical(f"output: {output}")
        # loop the output dict, get all of them into float
        for k, v in output.items():
            output[k] = float(v)
            # and get it to decimal 2
            output[k] = round(output[k], 2)
        multi_modal_output = output.get("M", 0)
        result_profile["multi_modal_output"] = output
        logger.critical(f"multi_modal_output: {multi_modal_output}")
        return result_profile, latency_profile
