import time
# from openai import OpenAI
from pathlib import Path

import torch
from django.conf import settings

from authenticate.utils.get_logger import get_logger
from ml.ml_models.get_features import GetFeatures
from ml.ml_models.sentiment import SentimentAnalysis

models_dir = Path(settings.BASE_DIR) / "ml" / "ml_models" / "model_data"

logger = get_logger(__name__)


def trigger_model(text, audio, images):
    # 1. get the features
    get_features_obj = GetFeatures((models_dir / "bert_cn").as_posix())
    if not text or not audio or not images:
        logger.error("No text, audio or images provided")
        logger.error(f"text: {text is None}, audio: {audio is None}, images: {images is None}")
        return

    feature_video = get_features_obj.get_images_tensor(images)  # (n/5,709)
    feature_audio = get_features_obj.get_audio_embedding(audio)  # (94,33)
    feature_text = get_features_obj.get_text_embeddings(text)  # (n+2,768)
    logger.info(
        f"feature_video: {feature_video.shape}, feature_audio: {feature_audio.shape}, feature_text: {feature_text[1].shape}")

    # test
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # data
    model = SentimentAnalysis().to(device)

    model.load_state_dict(
        {k.replace('Model.', ''): v for k, v in torch.load(models_dir / "sa_sims.pth").items()},
        strict=False)

    feature_text_in = feature_text[1].unsqueeze(dim=0)
    feature_video_in = feature_video.unsqueeze(dim=0)
    feature_audio_in = feature_audio.unsqueeze(dim=0)
    output = model(feature_text_in, feature_audio_in, feature_video_in)
    # output = model(feature_text[1], feature_audio, feature_video)
    logger.info(f"output: {output}")
    multi_modal_output = output.get("M", 0)
    if multi_modal_output >= 0:
        out_text = '积极情绪:' + text
    else:
        out_text = '消极情绪:' + text

    logger.info(out_text)

    # openai api
    # completion = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system",
    #          "content": "你是一个富有情感的助手，你能根据提问者的不同情绪做出不同的回答,但如果情绪和问题是相同的，则答案也必须相同"},
    #         {"role": "user",
    #          "content": out_text}
    #     ],
    #     temperature=0.0
    # )
    # print('input', out_text)
    # print('system', completion.choices[0].message.content)
