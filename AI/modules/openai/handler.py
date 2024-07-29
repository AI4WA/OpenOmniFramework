import base64
from pathlib import Path
from typing import Optional

from openai import OpenAI

from models.parameters import (
    OpenAIGPT4OParameters,
    OpenAIGPT4OTextOnlyParameters,
    Speech2TextParameters,
    Text2SpeechParameters,
)
from models.task import ResultStatus, Task
from models.track_type import TrackType
from modules.speech_to_text.speech2text import Speech2Text
from utils.constants import CLIENT_DATA_FOLDER, DATA_DIR
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker

logger = get_logger(__name__)


class OpenAIHandler:
    def __init__(self):
        self.client = OpenAI()

    def handle_task(self, task: Task) -> Task:
        """
        Handle the task
        Args:
            task (Task): The task

        Returns:
            The task with the result
        """
        result_profile = {}
        latency_profile = {}
        TimeLogger.log_task(task, "start_openai")
        if "speech2text" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_speech2text")
            text = self.speech2text(task)
            TimeLogger.log(latency_profile, "end_openai_speech2text")
            result_profile["text"] = text
        if "openai_gpt_4o_text_and_image" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_gpt_4o")
            text = self.gpt_4o_text_and_images(task)
            TimeLogger.log(latency_profile, "end_openai_gpt_4o")
            result_profile["text"] = text
        if "openai_gpt_4o_text_only" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_gpt_4o")
            text = self.gpt_4o_text_only(task)
            TimeLogger.log(latency_profile, "end_openai_gpt_4o")
            result_profile["text"] = text
        if "openai_gpt_35" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_gpt_35")
            text = self.gpt_35(task)
            TimeLogger.log(latency_profile, "end_openai_gpt_35")
            result_profile["text"] = text
        if "text2speech" in task.task_name:
            TimeLogger.log(latency_profile, "start_openai_text2speech")
            audio_file_path = self.text2speech(task)
            TimeLogger.log(latency_profile, "end_openai_text2speech")
            result_profile["audio_file_path"] = audio_file_path.split("/")[-1]
        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        TimeLogger.log_task(task, "end_openai")
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
            with time_tracker(
                    "locate_audio_file",
                    task.result_json.latency_profile,
                    track_type=TrackType.TRANSFER.value,
            ):
                audio_file_path = Speech2Text.locate_audio_file(
                    params.uid, params.audio_index, params.end_time
                )

            logger.info(f"Transcribing audio file: {audio_file_path}")

            audio_file_path = Path(audio_file_path)
            if not audio_file_path.exists():
                logger.error(f"Audio file {audio_file_path} not found")
                return None
            with time_tracker(
                    "openai_stt",
                    task.result_json.latency_profile,
                    track_type=TrackType.MODEL.value,
            ):
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

    def gpt_4o_text_only(self, task: Task) -> str:
        """
        Get the text only
        Args:
            task:

        Returns:

        """
        params = OpenAIGPT4OTextOnlyParameters(**task.parameters)
        text = params.text
        prompt_template = params.prompt_template
        logger.info(f"Text: {text}")
        prompt = prompt_template.format(text=text)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        with time_tracker(
                "gpt-4o-call",
                task.result_json.latency_profile,
                track_type=TrackType.MODEL.value,
        ):
            res = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
        return res.choices[0].message.content

    def gpt_35(self, task: Task) -> Optional[str]:
        """
        Call OpenAI endpoints to convert speech to text
        Args:
            task (Task): The path to the audio file

        Returns:
            str: The transcribed text
        """

        try:
            logger.info(task.parameters)
            params = OpenAIGPT4OTextOnlyParameters(**task.parameters)
            text = params.text
            prompt_template = params.prompt_template
            logger.info(f"Text: {text}")
            prompt = prompt_template.format(text=text)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            with time_tracker(
                    "openai_gpt_35",
                    task.result_json.latency_profile,
                    track_type=TrackType.MODEL.value,
            ):
                res = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                )

            return res.choices[0].message.content
        except Exception as e:
            logger.error(f"Error locating audio file: {e}")
            return None

    def gpt_4o_text_and_images(self, task: Task) -> Optional[str]:
        """
        Get the text and images
        And then call the GPT-4o endpoints

        # we need to sample the images as it will be a lot of them

        Args:
            task (Task): The task

        Returns:

        """
        params = OpenAIGPT4OParameters(**task.parameters)
        text = params.text
        images_path_list = params.images_path_list
        sample_ratio = params.sample_ratio
        prompt_template = params.prompt_template
        logger.info(f"Text: {text}")

        # sample the images
        # so, we will only get the images for every sample_ratio images
        logger.info(f"Current length of images: {len(images_path_list)}")
        logger.debug(images_path_list)
        images_path_list = images_path_list[::sample_ratio]
        logger.info(f"Sampled length of images: {len(images_path_list)}")

        # read image data to the one gpt-4o can take, something like data:image/jpeg;base64
        with time_tracker(
                label="encode_images",
                profile=task.result_json.latency_profile,
                track_type=TrackType.TRANSFER.value,
        ):
            images = []
            for images_path in images_path_list:
                folder = CLIENT_DATA_FOLDER / images_path
                if not folder.exists():
                    continue
                for image_file in folder.iterdir():
                    images.append(self.encode_image(image_file))
        """
        messages = [
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "What’s in this image?"
                },
                {
                  "type": "image_url",
                  "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                  }
                }
              ]
            }
          ]
        """

        prompt = prompt_template.format(text=text)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        for image in images:
            messages[0]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                }
            )
        logger.debug(messages)
        # call gpt-4o
        with time_tracker(
                "gpt-4o-call",
                task.result_json.latency_profile,
                track_type=TrackType.MODEL.value,
        ):
            res = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
        return res.choices[0].message.content

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def text2speech(self, task: Task) -> Optional[str]:
        """
        Call OpenAI endpoints to convert text to speech
        Args:
            task (Task): The text to convert

        Returns:

        """
        params = Text2SpeechParameters(**task.parameters)
        text = params.text
        logger.info(f"Text: {text}")
        output_audio_file_path = DATA_DIR / "tts" / f"{task.id}.mp3"
        # if folder does not exist, create it
        output_audio_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_audio_file_path = output_audio_file_path.as_posix()

        with time_tracker(
                "openai_tts",
                task.result_json.latency_profile,
                track_type=TrackType.MODEL.value,
        ):
            res = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
            )
        with time_tracker(
                "save_audio",
                task.result_json.latency_profile,
                track_type=TrackType.TRANSFER.value,
        ):
            res.stream_to_file(output_audio_file_path)
        return output_audio_file_path
