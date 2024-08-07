from django.dispatch import receiver

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.manager import ClusterManager
from orchestrator.chain.models import TaskData
from orchestrator.chain.signals import completed_rag
from orchestrator.chain.utils import data_multimodal_conversation_log_context_rag

logger = get_logger(__name__)


@receiver(completed_rag)
def trigger_completed_rag(sender, **kwargs):  # noqa
    """
    This will create the response, which will be a text 2 text task
    And we will need to log this ResText
    """
    try:
        logger.info("RAG completed triggerred")
        data = kwargs.get("data", {})
        track_id = kwargs.get("track_id", None)
        logger.info(data)
        task_data = TaskData(**data)

        if track_id is None:
            logger.error("No track_id found")
            return

        text = task_data.result_json["result_profile"]["text"]
        # then we need to locate the conversation task
        data_multimodal_conversation_log_context_rag(
            task_data=task_data,
            result=task_data.result_json["result_profile"],
        )
        data_text_id = task_data.parameters.get("data_text_id", None)
        ClusterManager.chain_next(
            track_id=track_id,
            current_component="completed_rag",
            next_component_params={"text": text, "data_text_id": data_text_id},
            user=sender.user,
        )

    except Exception as e:
        logger.exception(e)
        return
