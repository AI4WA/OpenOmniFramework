import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

import cv2
import torch
from django.conf import settings

from authenticate.utils.get_logger import get_logger
from hardware.models import AudioData, VideoData
from ml.ml_models.get_features import GetFeatures
from ml.ml_models.sentiment import SentimentAnalysis

models_dir = Path(settings.BASE_DIR) / "ml" / "ml_models" / "model_data"

logger = get_logger(__name__)


def gather_data():
    # get the audio data, which have not been process and have the text information
    audio_data: object = (
        AudioData.objects.filter(reaction__isnull=True).order_by("-created_at").first()
    )
    if audio_data is None:
        logger.info("No audio data found")
        return None, None, None, None
    text = audio_data.text

    audio_file = (
        settings.CLIENT_DATA_FOLDER
        / "Listener"
        / "data"
        / "audio"
        / audio_data.uid
        / "audio"
        / audio_data.audio_file
    ).as_posix()

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
    return text, [audio_file], image_np_list, audio_data


def trigger_model(text, audio, images) -> Optional[str]:
    # 1. get the features with bert cn model
    get_features_obj = GetFeatures((models_dir / "bert_cn").as_posix())
    if (not text) and (not audio) and (not images):
        logger.error("No text, audio and images provided")
        logger.error(
            f"text: {text is None}, audio: {audio is None}, images: {images is None}"
        )
        return
    if not text:
        logger.info("No text")
    if not audio:
        logger.info("No audio")
    if not images:
        logger.info("No image")

    feature_video = (
        get_features_obj.get_images_tensor(images) if images is not None else None
    )  # (n/5,709)
    feature_audio = (
        get_features_obj.get_audio_embedding(audio) if audio is not None else None
    )  # (94,33)
    #input raw text into the model 
    # feature_text = (
    #     get_features_obj.get_text_embeddings(text) if text is not None else None
    # )  # (n+2,768)
    # logger.info( f"feature_video: {feature_video.shape}, feature_audio: {feature_audio.shape}, feature_text: {
    # feature_text[1].shape}" )

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
    multi_modal_output = output.get("M", 0)
    logger.critical(f"multi_modal_output: {multi_modal_output}")
    return output
