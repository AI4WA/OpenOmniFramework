from authenticate.utils.get_logger import get_logger
from hardware.models import (
    ContextEmotionDetection,
    DataText,
    ResSpeech,
    ResText,
    ContextRAG,
)
from orchestrator.chain.models import TaskData

logger = get_logger(__name__)


def data_multimodal_conversation_log_res_text(task_data: TaskData, text: str):
    """
    Log the ResText to the DataMultiModalConversation

    Args:
        task_data (TaskData): The task data
        text (str): The text to log
    """
    res_text = ResText.objects.create(text=text)
    data_text_id = task_data.parameters.get("data_text_id", None)
    if data_text_id is not None:
        data_text = DataText.objects.filter(id=data_text_id).first()
        if data_text is not None and hasattr(data_text, "multi_modal_conversation"):
            data_text.multi_modal_conversation.res_text = res_text
            data_text.multi_modal_conversation.save()


def data_multimodal_conversation_log_res_speech(
    task_data: TaskData, speech_file_path: str
):
    """

    Args:
        task_data (TaskData): the task data
        speech_file_path (str): the speech file path

    Returns:

    """
    res_speech = ResSpeech.objects.create(text2speech_file=speech_file_path)
    data_text_id = task_data.parameters.get("data_text_id", None)
    if data_text_id is not None:
        data_text = DataText.objects.filter(id=data_text_id).first()
        if data_text is not None and hasattr(data_text, "multi_modal_conversation"):
            data_text.multi_modal_conversation.res_speech = res_speech
            data_text.multi_modal_conversation.save()


def data_multimodal_conversation_log_context_emotion_detection(
    task_data: TaskData, result: dict, logs: dict = None
):
    """

    Args:
        task_data (TaskData): the task data
        result (dict): the result of the context emotion detection
        logs (dict): the logs of the context emotion detection

    Returns:

    """
    data_text_id = task_data.parameters.get("data_text_id", None)
    if data_text_id is not None:
        data_text = DataText.objects.filter(id=data_text_id).first()
        if data_text is not None and hasattr(data_text, "multi_modal_conversation"):
            emotion = ContextEmotionDetection(
                multi_modal_conversation=data_text.multi_modal_conversation,
                result=result,
                logs=logs,
            )
            emotion.save()
            logger.info(emotion)


def data_multimodal_conversation_log_context_rag(
    task_data: TaskData, result: dict, logs: dict = None
):
    """

    Args:
        task_data (TaskData): the task data
        result (dict): the result of the context rag
        logs (dict): the logs of the context rag

    Returns:

    """
    data_text_id = task_data.parameters.get("data_text_id", None)
    if data_text_id is not None:
        data_text = DataText.objects.filter(id=data_text_id).first()
        if data_text is not None and hasattr(data_text, "multi_modal_conversation"):
            rag = ContextRAG(
                multi_modal_conversation=data_text.multi_modal_conversation,
                result=result,
                logs=logs,
            )
            rag.save()
            logger.info(rag)
