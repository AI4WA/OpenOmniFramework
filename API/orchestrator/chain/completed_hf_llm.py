from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_hf_llm

logger = get_logger(__name__)


@receiver(completed_hf_llm)
def trigger_completed_hf_llm(sender, **kwargs):  # noqa
    """
    This will create the response, which will be a text 2 text task
    """
    try:
        logger.info("HF LLM completed triggerred")
        data = kwargs.get("data", {})
        track_id = kwargs.get("track_id", None)
        logger.info(data)
        task_data = TaskData(**data)

        if track_id is None:
            logger.error("No track_id found")
            return

        text = task_data.result_json["result_profile"]["text"]

        ClusterManager.chain_next(
            track_id=track_id,
            current_component="completed_hf_llm",
            next_component_params={"text": text},
        )

    except Exception as e:
        logger.exception(e)
        return
