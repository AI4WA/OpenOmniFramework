from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_hf_llm
from orchestrator.chain.utils import data_multimodal_conversation_log_res_text

logger = get_logger(__name__)


@receiver(completed_hf_llm)
def trigger_completed_hf_llm(sender, **kwargs):  # noqa
    """
    This will create the response, which will be a text 2 text task
    We will create the ResText here
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
        # grab the multi-modal conversation
        data_multimodal_conversation_log_res_text(
            task_data=task_data,
            text=text,
        )
        data_text_id = task_data.parameters.get("data_text_id", None)
        ClusterManager.chain_next(
            track_id=track_id,
            current_component="completed_hf_llm",
            next_component_params={"text": text, "data_text_id": data_text_id},
            user=sender.user,
        )

    except Exception as e:
        logger.exception(e)
        return
