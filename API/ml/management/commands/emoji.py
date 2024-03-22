import os
import time

from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from hardware.models import AudioData, ReactionToAudio, Text2Speech, VideoData
from llm.llm_call.config import MT_CHATGLM, MT_LLAMA
from llm.llm_call.llm_adaptor import LLMAdaptor
from llm.models import LLMConfigRecords
from ml.ml_models.emoji_detect import gather_data, trigger_model

logger = get_logger(__name__)

DEFAULT_LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "llama2-7b-chat")


class Command(BaseCommand):
    help = 'Run the worker to finish the llm or stt tasks.'

    def add_arguments(self, parser):
        """
        Add arguments to the command
        """
        parser.add_argument('--llm_model_name', type=str,
                            help='The name of the llm model used to generate the response',
                            default=DEFAULT_LLM_MODEL_NAME)

    def handle(self, *args, **options):
        """
        Grab all the images/text/audio from the database and run the emotion detection model on them

        """
        llm_model_name = options['llm_model_name']
        llm_model_record = LLMConfigRecords.objects.filter(model_name=llm_model_name).first()
        if not llm_model_record:
            logger.error(f"Model {llm_model_name} not found in the database")
            return
        while True:
            text, audio_file, image_np_list, audio_obj = gather_data()
            try:
                emotion_output = trigger_model(text, audio_file, image_np_list)
                logger.info(f"Emotion output: {emotion_output}")
            except Exception as e:
                logger.error(f"Error: {e}")
                ReactionToAudio.objects.create(
                    audio=audio_obj,
                    failed=True,
                    failed_reason=str(e)
                )
                continue
            try:
                # the next step is to trigger the llm model
                adaptor = LLMAdaptor(llm_model_record.model_name)
                if emotion_output is None:
                    emotion_signal = "未知的"
                else:
                    emotion_signal = "积极的" if emotion_output.get("M", 0) > 0 else "消极的"
                prompt = (
                    f"你是个情感陪伴机器人，用相同的语言回答下面的问题。你发现你的主人的情绪是：{emotion_signal}。他说了句话：{text}。你会怎么回答？ "
                    f"你的回答是：")
                llm_response = adaptor.create_chat_completion(prompt)
                logger.info(f"LLM response: {llm_response}")
                ReactionToAudio.objects.create(
                    audio=audio_obj,
                    react_already=True,
                    emotion_result=emotion_output,
                    llm_response=llm_response
                )
                if llm_model_record.model_type == MT_LLAMA:
                    llm_res_text = llm_response["choices"][0]["message"]["content"]
                elif llm_model_record.model_type == MT_CHATGLM:
                    llm_res_text = llm_response["content"]
                else:
                    raise ValueError(f"Model type {llm_model_record.model_type} not supported")
                Text2Speech.objects.create(
                    hardware_device_mac_address=audio_obj.hardware_device_mac_address,
                    text=llm_res_text
                )

            except Exception as e:
                logger.error(f"Error: {e}")
                logger.exception(e)
                ReactionToAudio.objects.create(
                    audio=audio_obj,
                    failed=True,
                    failed_reason=str(e)
                )
                return

            time.sleep(1)
            logger.info("Emoji running...")
