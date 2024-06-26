from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.cluster import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_quantization_llm
from orchestrator.models import Task

logger = get_logger(__name__)


@receiver(completed_quantization_llm)
def trigger_completed_quantization_llm(sender, **kwargs):
    """
    This will create the response, which will be a text2text task
    """
    try:
        logger.info("Quantization LLM completed triggerred")
        data = kwargs.get("data", {})
        track_id = kwargs.get("track_id", None)
        logger.info(data)
        task_data = TaskData(**data)

        if track_id is None:
            logger.error("No track_id found")
            return

        text = task_data.result_json["result_profile"]["text"]
        Task.create_task(
            user=task_data.user_id,
            name="text2speech",
            task_name="text2speech",
            parameters={"text": text},
            track_id=track_id,
        )

    except Exception as e:
        logger.exception(e)
        return
