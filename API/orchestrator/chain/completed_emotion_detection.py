from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from hardware.models import ContextEmotionDetection
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_emotion_detection
from orchestrator.chain.utils import (
    data_multimodal_conversation_log_context_emotion_detection,
)

logger = get_logger(__name__)


@receiver(completed_emotion_detection)
def trigger_completed_emotion_detection(sender, **kwargs):
    """
    This will create a task to do the quantization LLM inference

    """
    try:
        logger.info("Emotion detection completed triggerred")
        data = kwargs.get("data", {})
        track_id = kwargs.get("track_id", None)
        logger.info(data)
        task_data = TaskData(**data)

        if track_id is None:
            logger.error("No track_id found")
            return
        data_text_id = task_data.parameters.get("data_text_id", None)

        # get the text and emotion from the result
        text = task_data.parameters["text"]
        emotion = task_data.result_json["result_profile"].get("multi_modal_output", {})
        data_multimodal_conversation_log_context_emotion_detection(
            task_data=task_data, result=emotion
        )
        emotion_text = (
            "Emotion value is from -1 to 1, -1 means negative, 1 means positive\n"
        )

        for key, value in emotion.items():
            if key == "A":
                emotion_text += f"Audio emotion: {value}\n"
            if key == "T":
                emotion_text += f"Text emotion: {value}\n"
            if key == "V":
                emotion_text += f"Video emotion: {value}\n"
            if key == "M":
                emotion_text += f"Overall emotion: {value}\n"
        prompt = f"""
            You are a conversational AI.
            Your friend said: {text}.
            And his emotion is detected like this:
            {emotion_text}
            
            Respond to him.
            Your response will directly send to him.
            
            """

        ClusterManager.chain_next(
            track_id=track_id,
            current_component="completed_emotion_detection",
            next_component_params={"text": prompt, "data_text_id": data_text_id},
            user=sender.user,
        )

    except Exception as e:
        logger.exception(e)
