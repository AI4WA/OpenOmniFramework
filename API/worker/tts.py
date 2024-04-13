import torchaudio
from django.conf import settings
from openai import OpenAI
from tortoise import api

from authenticate.utils.get_logger import get_logger
from hardware.models import Text2Speech

logger = get_logger(__name__)


class TTS:
    SUPPORTED_MODELS = ["tortoise-tts"]

    def __init__(self, model_name: str = "openai"):
        """
        Initialize the STT object
        """
        self.tts = api.TextToSpeech(use_deepspeed=True, kv_cache=True)
        self.model_name = model_name

    def handle_task(self, task):
        """
        Process the task
        :param task: The task to process
        :return: The result of the task
        """
        text = task.parameters["text"]
        logger.info(f"Text to speech: {text}")
        tts_obj_id = task.parameters["tts_obj_id"]

        text2speech_obj = Text2Speech.objects.filter(id=tts_obj_id).first()
        if text2speech_obj is None:
            logger.error(f"Text2Speech object not found with id {tts_obj_id}")
            return

        if self.model_name == "tortoise-tts":
            text2speech_audio = self.tts.tts_with_preset(
                text=text2speech_obj.text, preset="ultra_fast"
            )
            logger.info(f"Text2Speech audio: {text2speech_audio}")
            torchaudio.save(
                (
                    settings.CLIENT_DATA_FOLDER
                    / "Responder"
                    / "data"
                    / f"{tts_obj_id}.wav"
                ).as_posix(),
                text2speech_audio.squeeze(0).cpu(),
                24000,
            )
            text2speech_obj.text2speech_file = f"{tts_obj_id}.wav"
            text2speech_obj.save()
        elif self.model_name == "openai":
            self.text_to_speech_openai(text2speech_obj)
        return True

    def text_to_speech_openai(self, text2speech_obj: Text2Speech):
        audio_file_path = (
            settings.CLIENT_DATA_FOLDER
            / "Responder"
            / "data"
            / f"{text2speech_obj.id}.mp3"
        ).as_posix()

        client = OpenAI()

        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text2speech_obj.text,
        )
        response.stream_to_file(audio_file_path)
        text2speech_obj.text2speech_file = f"{text2speech_obj.id}.mp3"
        text2speech_obj.save()
        self.upload_to_s3(audio_file_path, f"tts/{text2speech_obj.id}.mp3")

    @staticmethod
    def upload_to_s3(file_path: str, s3_key: str):
        """
        Upload the file to S3
        :param file_path: The file path
        :param s3_key: The S3 key
        :return: The S3 URL
        """
        s3_client = settings.BOTO3_SESSION.client("s3")
        s3_client.upload_file(
            file_path,
            settings.CSV_BUCKET,
            s3_key,
        )
