import json
import os
import time

from django.core.management.base import BaseCommand
from worker.models import Task

from authenticate.utils.get_logger import get_logger
from hardware.models import EmotionDetection, LLMResponse, Text2Speech
from llm.models import LLMConfigRecords
from ml.ml_models.emoji_detect import gather_data, trigger_model

logger = get_logger(__name__)

DEFAULT_LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "llama2-7b-chat")


class Command(BaseCommand):
    help = "Run the worker to finish the llm or stt tasks."

    def add_arguments(self, parser):
        """
        Add arguments to the command
        """
        parser.add_argument(
            "--llm_model_name",
            type=str,
            help="The name of the llm model used to generate the response",
            default=DEFAULT_LLM_MODEL_NAME,
        )

    def handle(self, *args, **options):
        """
        Grab all the images/text/audio from the database and run the emotion detection model on them

        """
        llm_model_name = options["llm_model_name"]
        llm_model_record = LLMConfigRecords.objects.filter(
            model_name=llm_model_name
        ).first()
        if not llm_model_record:
            logger.error(f"Model {llm_model_name} not found in the database")
            return
        while True:
            text, audio_file, image_np_list, data_text = gather_data()
            if data_text is None:
                logger.info("No text to act on found")
                time.sleep(1)
                continue
            # mark this one as triggered
            data_text.pipeline_triggered = True
            data_text.save()
            try:
                emotion_output = trigger_model(text, audio_file, image_np_list)
                logger.info(f"Emotion output: {emotion_output}")
                emotion_detection = EmotionDetection(
                    home=data_text.home, data_text=data_text, result=emotion_output
                )
                emotion_detection.save()

            except Exception as e:
                logger.error(f"Error: {e}")
                emotion_detection = EmotionDetection(
                    home=data_text.home, data_text=data_text, logs={"error": str(e)}
                )
                emotion_detection.save()
                continue
            try:
                # the next step is to trigger the llm model
                if emotion_output is None:
                    emotion_signal = " You customer emotion is unknown."
                else:
                    emotion_signal = f"""
                    For emotion, we have value to measure it, 0 is neutral, -1 is negative, 1 is positive.
                    It scales from -1 to 1,
                    You customer emotion is {emotion_output}
                    """
                # Here we can load chat history
                prompt = f"""You are an aged care robot, {emotion_signal}.
                        He just said：{text}.
                        You reply will be? It will directly play back to the user.
                    """

                # create a task for the llm model, and then check for result
                user = data_text.home.user if data_text.home else None
                task = Task(
                    user=user,
                    name=f"Jarv5",
                    work_type="gpu",
                    parameters={
                        "model_name": llm_model_name,
                        "prompt": prompt,
                        "llm_task_type": "chat_completion",
                    },
                )
                task.save()
                # wait for the result
                while True:
                    task.refresh_from_db()
                    if task.result_status == "completed":
                        break
                    time.sleep(1)

                # get the result
                llm_response = task.description

                logger.info(f"LLM response: {llm_response}")
                llm_response_text = json.loads(llm_response)["choices"][0]["message"][
                    "content"
                ]
                llm_response_obj = LLMResponse(
                    home=data_text.home,
                    data_text=data_text,
                    messages=prompt,
                    result=llm_response_text,
                    logs={"llm_response": llm_response},
                )
                llm_response_obj.save()

                text2speech_obj = Text2Speech.objects.create(
                    home=data_text.home,
                    data_text=data_text,
                    text=llm_response_text,
                )
                # queue a task to tts
                tts_task = Task(
                    user=user,
                    name="Jarv5 TTS",
                    work_type="tts",
                    parameters={
                        "text": llm_response_text,
                        "tts_obj_id": text2speech_obj.id,
                    },
                )
                tts_task.save()

            except Exception as e:
                logger.error(f"Error: {e}")
                logger.exception(e)
                llm_response_obj = LLMResponse(
                    home=data_text.home,
                    data_text=data_text,
                    logs={"error": str(e)},
                )
                llm_response_obj.save()
                return

            time.sleep(1)
            logger.info("Emoji running...")

#
#
#
# def gather_data():
#     # get the audio data, which have not been process and have the text information
#     data_text = (
#         DataText.objects.filter(pipeline_triggered=False)
#         .order_by("-created_at")
#         .first()
#     )
#     if data_text is None:
#         logger.info("No text to act on found")
#         return None, None, None, None
#     text = data_text.text
#
#     data_audio = data_text.audio
#
#     audio_file = (
#         settings.CLIENT_DATA_FOLDER
#         / "Listener"
#         / "data"
#         / "audio"
#         / data_audio.uid
#         / "audio"
#         / data_audio.audio_file
#     ).as_posix()
#
#     # get the image data based on the audio data time range
#     # TODO: this will be changed rapidly
#     start_time = data_audio.start_time
#     end_time = data_audio.end_time
#     # round the start to the minute level down
#     start_time = start_time.replace(second=0, microsecond=0)
#     # round the end to the minute level up
#     end_time = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
#     logger.info(f"Start time: {start_time}, End time: {end_time}")
#     logger.info(data_audio)
#     # we will assume it comes from the same device
#     # list all videos has overlap with [start_time, end_time]
#     videos_data = DataVideo.objects.filter(
#         video_record_minute__range=[start_time, end_time]
#     )
#
#     images_path = []
#     for video_data in videos_data:
#         image_folder_name = video_data.video_file.split(".")[0].rsplit("-", 1)[0]
#         images_path.append(f"{video_data.uid}/frames/{image_folder_name}")
#
#     # I need to read image files into List[np.ndarray]
#     image_np_list = []
#     for image_path in images_path:
#         # loop the path, get all images
#         folder = (
#             settings.CLIENT_DATA_FOLDER / "Listener" / "data" / "videos" / image_path
#         )
#
#         if not folder.exists():
#             continue
#         for image_file in os.listdir(folder):
#             image = cv2.imread((folder / image_file).as_posix())
#             image_np_list.append(image)
#
#     # trigger the model
#     logger.info(f"Text: {text}, Audio: {audio_file}, Images: {len(image_np_list)}")
#
#     # sometimes there are no image information. judge if the image_np_list has zero data
#     image_np_list = None if len(image_np_list) == 0 else image_np_list
#
#     trigger_model(text, [audio_file], image_np_list)
#     return text, [audio_file], image_np_list, data_text
#
