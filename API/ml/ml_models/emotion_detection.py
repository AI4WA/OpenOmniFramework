# built-in dependencies
import argparse
import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
from ml.ml_models.get_features import GetFeatures
import torch

from openai import OpenAI

from ml.ml_models.sentiment import SentimentAnalysis

client = OpenAI(api_key='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')
work_path = ""
openface_path = 'D:/applications/anaconda/openface/FeatureExtraction.exe'
bert_path = 'pre-trained models/bert_cn'


def trigger_model(text, audio, images):  # 数据分析  images_index
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden_size", default=64, type=int)
    parser.add_argument("--mid_size", default=768, type=int)
    parser.add_argument("--pretrained", default="bert-base-uncased", type=str)
    parser.add_argument("--head_sa", default=4, type=int)
    parser.add_argument("--head_ga", default=8, type=int)
    parser.add_argument("--dropout_m", default=0.5, type=float)
    parser.add_argument("--dropout_f", default=0.7, type=float)
    parser.add_argument("--outdim", default=512, type=int)
    parser.add_argument("--output_size", default=1, type=int)
    parser.add_argument("--dropout", default=0.5, type=float)
    parser.add_argument("--act", default='relu', type=str)
    parser.add_argument("--num_loop", default=1, type=int)
    parser.add_argument("--feature_dims", default=[768, 33, 709], type=list)  # t,a,v
    args = parser.parse_args()

    images_index = 1
    time.sleep(2)

    if text and audio and images:

        feature_V = gf.handleImages(images)  # (n/5,709)
        feature_A = gf.getAudioEmbedding(audio)  # (94,33)
        feature_T = gf.getTextEmbedding(text)  # (n+2,768)

        # test

        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        # data
        model = SentimentAnalysis(args).to(device)

        # a =  model.load_state_dict(torch.load("pre-trained models/taskw-mosei_3part.pth"))
        # print(a['Model.'])

        model.load_state_dict(
            {k.replace('Model.', ''): v for k, v in torch.load("pre-trained models/taskw-sims.pth").items()},
            strict=False)
        # model.load_state_dict(torch.load("pre-trained models/taskw-mosei_3part.pth"))
        output = model(feature_T, feature_A, feature_V)

        images_index = images_index + 1

        if output >= 0:
            out_text = '积极情绪:' + text
        else:
            out_text = '消极情绪:' + text

        # openai api
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "你是一个富有情感的助手，你能根据提问者的不同情绪做出不同的回答,但如果情绪和问题是相同的，则答案也必须相同"},
                {"role": "user",
                 "content": out_text}
            ],
            temperature=0.0
        )
        print('input', out_text)
        print('system', completion.choices[0].message.content)
        streamed_audio(completion.choices[0].message.content, "tts-1", "alloy")
        print("next loop")


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)  # 打开默认摄像头
    num_img = 20
    images = []

    i = 0
    while i < num_img:
        ret, frame = cap.read()  # 读取帧
        if not ret:
            break

        # 在这里，你可以对frame进行预处理，比如调整大小等。
        images.append(frame)

        # 显示摄像头帧
        cv2.imshow('Frame', frame)
        i += 1
        cv2.waitKey(1000)

    cap.release()
    cv2.destroyAllWindows()

    gf = GetFeatures("", '', '')
    gf.handleImages(images[10:20])
