from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_openai_gpt_4o_text_only

logger = get_logger(__name__)


@receiver(completed_openai_gpt_4o_text_only)
def trigger_completed_openai_gpt_4o_text_only(sender, **kwargs):  # noqa
    """
    This will create the response, which will be a text 2 text task
    """
    try:
        logger.info("OpenAI GPT 4o LLM completed triggerred")
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
            current_component="completed_openai_gpt_4o_text_only",
            next_component_params={"text": text},
            user=sender.user,
        )

    except Exception as e:
        logger.exception(e)
        return
