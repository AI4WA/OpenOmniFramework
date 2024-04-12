import json
import os
import time

from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from hardware.models import EmotionDetection, LLMResponse, Text2Speech
from llm.models import LLMConfigRecords
from ml.ml_models.emoji_detect import gather_data, trigger_model
from worker.models import Task

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
                    emotion_signal = "未知的"
                else:
                    emotion_signal = (
                        "积极的" if emotion_output.get("M", 0) > 0 else "消极的"
                    )
                # Here we can load chat history
                prompt = (
                    f"你是个情感陪伴机器人，用相同的语言回答下面的问题。你发现你的主人的情绪是：{emotion_signal}。他说了句话：{text}。你会怎么回答？ "
                    f"你的回答是："
                )

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
                    messages=llm_response,
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
