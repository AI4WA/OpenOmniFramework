from typing import Optional

import torch
from modules.emotion_detection.features_extraction import FeaturesExtractor
from modules.emotion_detection.sentiment import SentimentAnalysis
from utils.constants import EMOTION_DETECTION_MODEL_DIR
from utils.get_logger import get_logger

models_dir = EMOTION_DETECTION_MODEL_DIR / "model_data"

logger = get_logger(__name__)


def trigger_model(text, audio, images) -> Optional[dict]:
    # 1. get the features with bert cn model
    features_extractor = FeaturesExtractor()
    if not text or not audio or not images:
        logger.error("No text, audio or images provided")
        logger.error(
            f"text: {text is None}, audio: {audio is None}, images: {images is None}"
        )
        return

    feature_video = (
        features_extractor.get_images_tensor(images) if images is not None else None
    )  # (n/5,709)
    feature_audio = (
        features_extractor.get_audio_embedding(audio) if audio is not None else None
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
    model.load_state_dict(
        {
            k.replace("Model.", ""): v
            for k, v in torch.load(models_dir / "sa_sims.pth").items()
        },
        strict=True,
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
