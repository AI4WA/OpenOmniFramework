from datetime import datetime
from typing import Optional

from openai import OpenAI

from models.parameters import Text2SpeechParameters
from models.task import Task
from utils.aws import BOTO3_SESSION, CSV_BUCKET
from utils.constants import DATA_DIR
from utils.get_logger import get_logger

logger = get_logger(__name__)


class Text2Speech:

    def __init__(self, model_name: str = "openai", to_s3: bool = False):
        """
        Initialize the STT object

        Args:
            model_name (str): The name of the model to use
            to_s3 (bool): If the audio file should be uploaded to S3
        """

        self.tts = None
        self.model_name = model_name
        self.to_s3 = to_s3

    def handle_task(self, task: Task) -> Optional[Task]:
        """
        Args:
            task (Task): The task to handle

        Returns:
            The task with the result
        """
        text2speech_parameters = Text2SpeechParameters(**task.parameters)
        logger.info(f"Text to speech: {text2speech_parameters.text}")

        if self.model_name == "openai":
            return self.text_to_speech_openai(
                task=task, task_param=text2speech_parameters
            )
        return None

    def text_to_speech_openai(
        self, task: Task, task_param: Text2SpeechParameters
    ) -> Task:
        """
        Convert the text to speech using OpenAI API
        Args:
            task (Task): The task to handle
            task_param (Text2SpeechParameters): The parameters for the task

        Returns:

        """
        result_profile = {}
        latency_profile = {}
        audio_file_path = DATA_DIR / "tts" / f"{task.id}.mp3"
        # if folder does not exist, create it
        audio_file_path.parent.mkdir(parents=True, exist_ok=True)
        audio_file_path = audio_file_path.as_posix()

        client = OpenAI()
        start_time = datetime.now()
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=task_param.text,
        )
        latency_profile["model_openai_tts"] = (
            datetime.now() - start_time
        ).total_seconds()
        start_time = datetime.now()
        response.stream_to_file(audio_file_path)
        latency_profile["transfer_save_audio"] = (
            datetime.now() - start_time
        ).total_seconds()
        result_profile["audio_file_path"] = audio_file_path

        start_time = datetime.now()
        if self.to_s3:
            self.upload_to_s3(audio_file_path, f"tts/{task.id}.mp3")
        latency_profile["transfer_to_s3"] = (
            datetime.now() - start_time
        ).total_seconds()

        task.result_status = "completed"
        task.result_json = {
            "result_profile": result_profile,
            "latency_profile": latency_profile,
        }
        return task

    @staticmethod
    def upload_to_s3(file_path: str, s3_key: str):
        """
        Upload the file to S3
        Args:
            file_path (str): The path to the file
            s3_key (str): The key to use in S3

        """
        s3_client = BOTO3_SESSION.client("s3")
        s3_client.upload_file(
            file_path,
            CSV_BUCKET,
            s3_key,
        )
