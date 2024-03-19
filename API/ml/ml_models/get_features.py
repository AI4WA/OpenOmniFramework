from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import librosa
import numpy as np
import torch
from deepface.commons.logger import Logger
from deepface.detectors import DetectorWrapper
from deepface.models.Detector import DetectedFace, FacialAreaRegion
from deepface.models.FacialRecognition import FacialRecognition
from deepface.modules import modeling, preprocessing
from PIL import Image
from tensorflow.keras.preprocessing import image
from transformers import BertModel, BertTokenizer

from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)


class GetFeatures:

    def __init__(self, pretrained_bert_dir: str) -> None:
        self.padding_mode = 'zeros'
        self.padding_location = 'back'
        self.pretrained_bert_dir = pretrained_bert_dir

    def get_text_embeddings(self, text: str) -> Tuple[str, torch.Tensor]:
        """Returns embeddings for the given text using a BERT model."""
        tokenizer = BertTokenizer.from_pretrained(self.pretrained_bert_dir)
        model = BertModel.from_pretrained(self.pretrained_bert_dir)
        input_ids = torch.tensor([tokenizer.encode(text, add_special_tokens=True)])
        with torch.no_grad():
            last_hidden_states = model(input_ids)[0]
        return text, torch.tensor(last_hidden_states.squeeze().numpy()).float()

    @staticmethod
    def get_audio_embedding(audios: List[str]) -> torch.Tensor:
        """Extracts and returns average audio features from a list of audio files."""
        features = []
        for audio_path in audios:
            y, sr = librosa.load(audio_path)
            hop_length = 512
            f0 = librosa.feature.zero_crossing_rate(y, hop_length=hop_length).T
            mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, htk=True).T
            cqt = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length).T
            temp_feature = np.concatenate([f0, mfcc, cqt], axis=-1)
            features.append(temp_feature)
        feature = np.mean(np.concatenate(features), axis=0).reshape(1, -1)
        # get them into tensor
        feature = torch.tensor(feature).float()
        return feature

    def get_images_tensor(self, images: List[np.ndarray]) -> torch.Tensor:
        """Extracts features from a list of images using a specified model."""
        model_name = "OpenFace"
        image_features = [self.represent(image, model_name=model_name)[0]['embedding'] for image in images]
        return torch.tensor(image_features)

    def represent(
            self,
            img,
            model_name: str = "VGG-Face",
            enforce_detection: bool = False,
            detector_backend: str = "opencv",
            align: bool = True,
            expand_percentage: int = 0,
            normalization: str = "base",
    ) -> List[Dict[str, Any]]:
        resp_objs = []

        model: FacialRecognition = modeling.build_model(model_name)

        # ---------------------------------
        # we have run pre-process in verification. so, this can be skipped if it is coming from verifying.
        target_size = model.input_shape
        if detector_backend != "skip":
            img_objs = self.extract_faces(
                img,
                target_size=(target_size[1], target_size[0]),
                detector_backend=detector_backend,
                grayscale=False,
                enforce_detection=enforce_detection,
                align=align,
                expand_percentage=expand_percentage,
            )
        else:  # skip
            # --------------------------------
            if len(img.shape) == 4:
                img = img[0]  # e.g. (1, 224, 224, 3) to (224, 224, 3)
            if len(img.shape) == 3:
                img = cv2.resize(img, target_size)
                img = np.expand_dims(img, axis=0)
                # When called from verifying, this is already normalized. But needed when user given.
                if img.max() > 1:
                    img = (img.astype(np.float32) / 255.0).astype(np.float32)
            # --------------------------------
            # make dummy region and confidence to keep compatibility with `extract_faces`
            img_objs = [
                {
                    "face": img,
                    "facial_area": {"x": 0, "y": 0, "w": img.shape[1], "h": img.shape[2]},
                    "confidence": 0,
                }
            ]
        # ---------------------------------

        for img_obj in img_objs:
            img = img_obj["face"]
            region = img_obj["facial_area"]
            confidence = img_obj["confidence"]
            # custom normalization
            img = preprocessing.normalize_input(img=img, normalization=normalization)

            embedding = model.find_embeddings(img)

            resp_obj = {"embedding": embedding, "facial_area": region, "face_confidence": confidence}
            resp_objs.append(resp_obj)

        return resp_objs

    logger = Logger(module="deepface/modules/detection.py")

    @staticmethod
    def extract_faces(
            img,
            target_size: Optional[Tuple[int, int]] = (224, 224),
            detector_backend: str = "opencv",
            enforce_detection: bool = True,
            align: bool = False,
            expand_percentage: int = 0.2,
            grayscale: bool = False,
            human_readable=False,
    ) -> List[Dict[str, Any]]:
        resp_objs = []
        base_region = FacialAreaRegion(x=0, y=0, w=img.shape[1], h=img.shape[0], confidence=0)

        if detector_backend == "skip":
            face_objs = [DetectedFace(img=img, facial_area=base_region, confidence=0)]
        else:
            face_objs = DetectorWrapper.detect_faces(
                detector_backend=detector_backend,
                img=img,
                align=align,
                expand_percentage=expand_percentage,
            )
        # logger.info(f"Detected {len(face_objs)} faces.")
        # in case of no face found
        if len(face_objs) == 0 and enforce_detection is True:
            raise ValueError(
                "Face could not be detected. Please confirm that the picture is a face photo "
                "or consider to set enforce_detection param to False."
            )

        if len(face_objs) == 0 and enforce_detection is False:
            face_objs = [DetectedFace(img=img, facial_area=base_region, confidence=0)]

        for face_obj in face_objs:
            current_img = face_obj.img
            current_region = face_obj.facial_area

            if current_img.shape[0] == 0 or current_img.shape[1] == 0:
                continue

            if grayscale is True:
                current_img = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)

            # resize and padding
            if target_size is not None:
                factor_0 = target_size[0] / current_img.shape[0]
                factor_1 = target_size[1] / current_img.shape[1]
                factor = min(factor_0, factor_1)

                dsize = (
                    int(current_img.shape[1] * factor),
                    int(current_img.shape[0] * factor),
                )
                current_img = cv2.resize(current_img, dsize)

                diff_0 = target_size[0] - current_img.shape[0]
                diff_1 = target_size[1] - current_img.shape[1]
                if grayscale is False:
                    # Put the base image in the middle of the padded image
                    current_img = np.pad(
                        current_img,
                        (
                            (diff_0 // 2, diff_0 - diff_0 // 2),
                            (diff_1 // 2, diff_1 - diff_1 // 2),
                            (0, 0),
                        ),
                        "constant",
                    )
                else:
                    current_img = np.pad(
                        current_img,
                        (
                            (diff_0 // 2, diff_0 - diff_0 // 2),
                            (diff_1 // 2, diff_1 - diff_1 // 2),
                        ),
                        "constant",
                    )

                # double check: if target image is not still the same size with target.
                if current_img.shape[0:2] != target_size:
                    current_img = cv2.resize(current_img, target_size)

            # normalizing the image pixels
            # what this line doing? must?
            img_pixels = image.img_to_array(current_img)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255  # normalize input in [0, 1]
            # discard expanded dimension
            if human_readable is True and len(img_pixels.shape) == 4:
                img_pixels = img_pixels[0]

            resp_objs.append(
                {
                    "face": img_pixels[:, :, ::-1] if human_readable is True else img_pixels,
                    "facial_area": {
                        "x": int(current_region.x),
                        "y": int(current_region.y),
                        "w": int(current_region.w),
                        "h": int(current_region.h),
                        "left_eye": current_region.left_eye,
                        "right_eye": current_region.right_eye,
                    },
                    "confidence": round(current_region.confidence, 2),
                }
            )

        if len(resp_objs) == 0 and enforce_detection is True:
            raise ValueError(
                f"Exception while extracting faces from ...."
                "Consider to set enforce_detection arg to False."
            )

        return resp_objs

    @staticmethod
    def align_face(
            img: np.ndarray,
            left_eye: Union[list, tuple],
            right_eye: Union[list, tuple],
    ) -> Tuple[np.ndarray, float]:
        # if eye could not be detected for the given image, return the image itself
        if left_eye is None or right_eye is None:
            return img, 0

        # sometimes unexpectedly detected images come with nil dimensions
        if img.shape[0] == 0 or img.shape[1] == 0:
            return img, 0

        angle = float(np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0])))
        img = np.array(Image.fromarray(img).rotate(angle))
        return img, angle
