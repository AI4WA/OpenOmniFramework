from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.cluster import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_emotion_detection
from orchestrator.models import Task

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

        cluster_name = track_id.split("-")[1]

        next_component_name, next_component = ClusterManager.get_next(
            cluster_name, "completed_emotion_detection"
        )
        logger.info(next_component)

        if next_component is None:
            logger.error("No next component found")
            return

        if next_component_name == "completed_quantization_llm":
            # get the text and emotion from the result
            text = task_data.parameters["text"]
            emotion = task_data.result_json["result_profile"].get(
                "multi_modal_output", {}
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
            Task.create_task(
                user=task_data.user_id,
                name=f"quantization_llm",
                task_name="quantization_llm",
                parameters={
                    "prompt": prompt,
                    **next_component["extra_params"],
                },
                track_id=track_id,
            )
    except Exception as e:
        logger.exception(e)
