import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

import cv2
import torch
from django.conf import settings

from authenticate.utils.get_logger import get_logger
from hardware.models import DataAudio, DataText, DataVideo
from ml.ml_models.get_features import GetFeatures
from ml.ml_models.sentiment import SentimentAnalysis

models_dir = Path(settings.BASE_DIR) / "ml" / "ml_models" / "model_data"

logger = get_logger(__name__)


def gather_data():
    # get the audio data, which have not been process and have the text information
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

    audio_file = (
        settings.CLIENT_DATA_FOLDER
        / "Listener"
        / "data"
        / "audio"
        / data_audio.uid
        / "audio"
        / data_audio.audio_file
    ).as_posix()

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
    image_np_list = []
    for image_path in images_path:
        # loop the path, get all images
        folder = (
            settings.CLIENT_DATA_FOLDER / "Listener" / "data" / "videos" / image_path
        )

        if not folder.exists():
            continue
        for image_file in os.listdir(folder):
            image = cv2.imread((folder / image_file).as_posix())
            image_np_list.append(image)

    # trigger the model
    logger.info(f"Text: {text}, Audio: {audio_file}, Images: {len(image_np_list)}")
    trigger_model(text, [audio_file], image_np_list)
    return text, [audio_file], image_np_list, data_text


def trigger_model(text, audio, images) -> Optional[dict]:
    # 1. get the features with bert cn model
    get_features_obj = GetFeatures((models_dir / "bert_cn").as_posix())
    if not text or not audio or not images:
        logger.error("No text, audio or images provided")
        logger.error(
            f"text: {text is None}, audio: {audio is None}, images: {images is None}"
        )
        return

    feature_video = (
        get_features_obj.get_images_tensor(images) if images is not None else None
    )  # (n/5,709)
    feature_audio = (
        get_features_obj.get_audio_embedding(audio) if audio is not None else None
    )  # (94,33)
    logger.info(
        f"feature_video: {feature_video.shape}, feature_audio: {feature_audio.shape}"
    )

    # data is ready
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = SentimentAnalysis().to(device)
    # load the model
    model.load_state_dict(
        {
            k.replace("Model.", ""): v
            for k, v in torch.load(models_dir / "sa_sims.pth").items()
        },
        strict=False,
    )

    model.eval()

    # run model
    output = model(text, feature_audio, feature_video)
    logger.critical(f"output: {output}")
    # loop the output dict, get all of them into float
    for k, v in output.items():
        output[k] = float(v)
        # and get it to decimal 2
        output[k] = round(output[k], 2)
    multi_modal_output = output.get("M", 0)
    logger.critical(f"multi_modal_output: {multi_modal_output}")
    return output
