from pathlib import Path
from typing import Optional

from openai import OpenAI

from models.parameters import Speech2TextParameters
from models.task import Task
from modules.speech_to_text.speech2text import Speech2Text
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker

logger = get_logger(__name__)


class OpenAIHandler:
    def __init__(self):
        self.client = OpenAI()

    def handle_task(self, task: Task) -> Optional[Task]:
        """
        Handle the task
        Args:
            task (Task): The task

        Returns:
            The task with the result
        """
        result_profile = {}
        latency_profile = {}

        if "speech2text" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_speech2text")
            with time_tracker("openai_speech2text", latency_profile):
                text = self.speech2text(task)
            TimeLogger.log(latency_profile, "end_openai_speech2text")
            result_profile["text"] = text
        task.result_status = "completed"
        task.result_json["result_profile"] = result_profile
        task.result_json["latency_profile"] = latency_profile
        return task

    def speech2text(self, task: Task) -> Optional[str]:
        """
        Call OpenAI endpoints to convert speech to text
        Args:
            task (Task): The path to the audio file

        Returns:
            str: The transcribed text
        """

        try:
            logger.info(task.parameters)
            params = Speech2TextParameters(**task.parameters)
            audio_file_path = Speech2Text.locate_audio_file(
                params.uid, params.audio_index, params.end_time
            )

            logger.info(f"Transcribing audio file: {audio_file_path}")

            audio_file_path = Path(audio_file_path)
            if not audio_file_path.exists():
                logger.error(f"Audio file {audio_file_path} not found")
                return None
            with open(audio_file_path, "rb") as audio_file:
                res = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )

            text = res.text
            logger.info(f"Transcription result: {text}")
            return text
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
        return None
