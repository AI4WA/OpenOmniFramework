import torchaudio
from django.conf import settings
from tortoise import api

from authenticate.utils.get_logger import get_logger
from hardware.models import Text2Speech

logger = get_logger(__name__)

tts_model = api.TextToSpeech(use_deepspeed=True, kv_cache=True)


class TTS:
    SUPPORTED_MODELS = ["tortoise-tts"]

    def __init__(self):
        """
        Initialize the STT object
        """
        self.tts = tts_model

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

        text2speech_audio = self.tts.tts_with_preset(
            text=text2speech_obj.text, preset="ultra_fast"
        )
        logger.info(f"Text2Speech audio: {text2speech_audio}")
        torchaudio.save(
            (
                settings.CLIENT_DATA_FOLDER / "Responder" / "data" / f"{tts_obj_id}.wav"
            ).as_posix(),
            text2speech_audio.squeeze(0).cpu(),
            24000,
        )
        text2speech_obj.text2speech_file = f"{tts_obj_id}.wav"
        text2speech_obj.save()
        return True
    #
    # @staticmethod
    # def text_to_speech_openai(content: str,
    #                           model: str = "tts-1",
    #                           voice: str = "alloy"):
    #     # API endpoint URL
    #     url = "https://api.openai.com/v1/audio/speech"
    #
    #     # Headers with authorization
    #     headers = {
    #         "Authorization": f"Bearer {api_key}"
    #     }
    #
    #     # Request payload
    #     data = {
    #         "model": model,
    #         "input": content,
    #         "voice": voice,
    #         "response_format": "mp3"
    #     }
    #
    #     try:
    #         with timer(logger, "Request to OpenAI"):
    #             # Make a POST request to the OpenAI audio API
    #             response = requests.post(url, headers=headers, json=data, stream=True)
    #
    #         # Check if the request was successful
    #         if response.status_code == 200:
    #             # Use ffmpeg to convert the MP3 audio to WAV format in memory
    #             process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'wav', '-'], stdin=subprocess.PIPE,
    #                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #             wav_audio, ffmpeg_error = process.communicate(input=response.content)
    #             process.wait()
    #
    #             if process.returncode == 0:
    #                 # Convert the WAV audio bytes to AudioSegment
    #                 audio_content = AudioSegment.from_wav(io.BytesIO(wav_audio))
    #
    #                 # Play the audio
    #                 play(audio_content)
    #             else:
    #                 logger.info(f"FFmpeg error: {ffmpeg_error.decode()}")
    #         else:
    #             logger.error(f"Error: {response.status_code}\n{response.text}")
    #     except Exception as error:
    #         logger.error(f"Error in streamed_audio: {str(error)}")
