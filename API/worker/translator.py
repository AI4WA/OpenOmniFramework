import whisper
import torch
from django.conf import settings
from datetime import datetime
from authenticate.utils.get_logger import get_logger
from authenticate.utils.timer import timer
from hardware.models import AudioData

logger = get_logger(__name__)


class Translator:
    SUPPORTED_MODELS = ['whisper']

    def __init__(self, model_name: str = "whisper", model_size: str = 'base', multi_language: bool = False):
        """
        Initialize the translator
        :param model_name: The name of the model to use
        :param model_size: The size of the model to use
        :param multi_language: Whether to use a multi-language model
        """
        self.model_name = model_name
        if self.model_name == 'whisper':
            if not multi_language:
                model_size = f"{model_size}.en"
            self.audio_model = whisper.load_model(model_size)
        else:
            raise ValueError(f"Model {model_name} not supported")

    @staticmethod
    def locate_audio_file(uid: str, sequence_index: str, end_time: str):
        """
        Locate the audio file
        :param uid: The uid of the audio file
        :param sequence_index: The sequence index of the audio file

        :param end_time: The end time of the audio file, the file will name after this,
            format also like: "2024-03-13T13:10:21.527852Z"
        :return: The path to the audio file
        """
        audio_folder = settings.CLIENT_DATA_FOLDER / "Listener" / "audio" / uid / "audio"
        # audio file will be within this folder, and name like sequence_index-endtimetimestap.wav
        end_time_obj = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        audio_file = audio_folder / f"{sequence_index}-{end_time_obj.strftime('%Y%m%d%H%M%S')}.wav"
        if not audio_file.exists():
            logger.error(f"Audio file {audio_file} not found")
            raise FileNotFoundError(f"Audio file {audio_file} not found")
        return audio_file

    def translate(self, message):
        """

        """
        logger.info(f"Translating message {message}")
        # read the data from the audio file in .wav file, then do the translation
        audio_file = self.locate_audio_file(message['uid'],
                                            message['audio_index'],
                                            message['end_time'])
        logger.info(f"Audio file {audio_file}")
        if audio_file is None:
            return None, None

        with timer(logger, "Loading audio"):
            audio_np = whisper.load_audio(audio_file.as_posix())
        with timer(logger, "Transcribing"):
            result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
        logger.critical(result)
        return result, audio_file

    def handle_task(self, task):
        """
        :param task: The task to handle
        """
        try:
            result, audio_file = self.translate(task.parameters)
            task.result_status = "completed"
            task.description = result
            task.save()
            logger.info(f"Task {task.id} completed")
            logger.info(task.__dict__)
            AudioData.create_obj(
                uid=task.parameters['uid'],
                sequence_index=int(task.parameters['audio_index']),
                text=result['text'],
                audio_file=audio_file.as_posix().split("/")[-1],
                start_time=datetime.strptime(task.parameters['start_time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                end_time=datetime.strptime(task.parameters['end_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
            )
        except FileNotFoundError:
            # then we need to try later as the sync is not done yet
            logger.error(f"Audio file not found, will try later")
            task.result_status = "pending"
            task.save()
        except Exception as e:
            logger.error(e)
            task.result_status = "failed"
            task.description = str(e)
            task.save()
            logger.error(f"Task {task.id} failed")
            logger.error(e)
