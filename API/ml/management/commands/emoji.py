from django.core.management.base import BaseCommand
from llm.llm_call.llm_adaptor import LLMAdaptor
from authenticate.utils.get_logger import get_logger
from hardware.models import AudioData, VideoData, ReactionToAudio, Text2Speech
from ml.ml_models.emoji_detect import trigger_model, gather_data

logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Run the worker to finish the llm or stt tasks.'

    def handle(self, *args, **options):
        """
        Grab all the images/text/audio from the database and run the emotion detection model on them

        """
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
            return
        try:
            # next step is to trigger the llm model
            adaptor = LLMAdaptor("llama2-7b-chat")
            emotion_signal = "积极的" if emotion_output.get("M", 0) > 0 else "消极的"
            prompt = (f"你是个情感陪伴机器人，你发现你的主人的情绪是：{emotion_signal}。他说了句话：{text}。你会怎么回答？ "
                      f"你的回答是：")
            llm_response = adaptor.create_chat_completion(prompt)
            logger.info(f"LLM response: {llm_response}")
            ReactionToAudio.objects.create(
                audio=audio_obj,
                react_already=True,
                emotion_result=emotion_output,
                llm_response=llm_response
            )
            llm_res_text = llm_response[0]["text"]
            Text2Speech.objects.create(
                hardware_device_mac_address=audio_obj.hardware_device_mac_address,
                llm_res_text=llm_res_text
            )

        except Exception as e:
            logger.error(f"Error: {e}")
            ReactionToAudio.objects.create(
                audio=audio_obj,
                failed=True,
                failed_reason=str(e)
            )
            return
