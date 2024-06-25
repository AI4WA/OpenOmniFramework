from datetime import datetime
from typing import Tuple

import torch
import whisper

from models.parameters import Speech2TextParameters
from utils.constants import CLIENT_DATA_FOLDER
from utils.get_logger import get_logger
from utils.timer import timer

logger = get_logger(__name__)


class Speech2Text:
    SUPPORTED_MODELS = ["whisper"]

    def __init__(
        self,
        model_name: str = "whisper",
        model_size: str = "small",
        multi_language: bool = True,
    ):
        """
        Initialize the translator
        Args:
            model_name (str): The name of the model to use
            model_size (str): The size of the model to use
            multi_language (bool): If the model is multi-language
        """
        self.model_name = model_name
        if self.model_name == "whisper":
            if not multi_language and "large" not in model_size:
                model_size = f"{model_size}.en"
            self.audio_model = whisper.load_model(model_size)
        else:
            raise ValueError(f"Model {model_name} not supported")

    @staticmethod
    def locate_audio_file(uid: str, sequence_index: str, end_time: str):
        """
        Locate the audio file
        Args:
            uid (str): The uid
            sequence_index (str): The sequence index
            end_time (str): The end time

        Returns:
            The audio file (str): The audio file
        """
        audio_folder = CLIENT_DATA_FOLDER / "audio" / uid
        # audio file will be within this folder, and name like sequence_index-endtimetimestap.wav
        end_time_obj = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%f")
        audio_file = (
            audio_folder
            / f"{sequence_index}-{end_time_obj.strftime('%Y%m%d%H%M%S')}.wav"
        )
        if not audio_file.exists():
            logger.error(f"Audio file {audio_file} not found")
            raise FileNotFoundError(f"Audio file {audio_file} not found")
        return audio_file

    def translate(self, message: Speech2TextParameters) -> Tuple[dict, dict]:
        """
        This is the key function to translate the audio to text
        Args:
            message (dict): The message to translate

        Returns:
            str: The translated text
            latency_profile (dict): The latency profile

        """
        latency_profile = {}
        result_profile = {}
        logger.info(f"Translating message {message}")
        # read the data from the audio file in .wav file, then do the translation
        audio_file = self.locate_audio_file(
            message.uid, message.audio_index, message.end_time
        )
        logger.info(f"Audio file {audio_file}")
        if audio_file is None:
            return latency_profile, result_profile

        with timer(logger, "Loading audio"):
            start_time = datetime.now()
            audio_np = whisper.load_audio(audio_file.as_posix())
            latency_profile["model_load_audio"] = (
                datetime.now() - start_time
            ).total_seconds()
        with timer(logger, "Transcribing"):
            start_time = datetime.now()
            result_profile = self.audio_model.transcribe(
                audio_np, fp16=torch.cuda.is_available()
            )
            latency_profile["model_transcribe"] = (
                datetime.now() - start_time
            ).total_seconds()
        logger.critical(result_profile)
        return latency_profile, result_profile

    def handle_task(self, task):
        """
        Args:
            task: The task to process
        """
        try:
            start_time = datetime.now()
            task_parameters = Speech2TextParameters(**task.parameters)
            latency_profile, result_profile = self.translate(task_parameters)
            end_time = datetime.now()
            latency_profile["transfer_within_speech2text"] = (
                end_time - start_time
            ).total_seconds()
            task.result_status = "completed"
            task.result_json = {
                "result_profile": result_profile,
                "latency_profile": latency_profile,
            }
        except FileNotFoundError:
            # then we need to try later as the sync is not done yet
            logger.error("Audio file not found, will try later")
            task.result_status = "pending"
        except Exception as e:
            logger.error(e)
            task.result_status = "failed"
            task.description = str(e)
        return task
