from models.parameters import QuantizationLLMParameters
from models.task import ResultStatus, Task
from models.track_type import TrackType
from modules.quantization_llm.models import QuantizationLLMModelConfig
from utils.api import API
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker

from .adaptor_worker import QuantizationLLMAdaptor

logger = get_logger(__name__)


class QuantizationLLM:
    def __init__(self, api: API):
        """
        Here is used to load and manage the quantization LLM model

        Args:
            api (API): The API object to query the API
        """
        # query the available models
        # init for llm models
        self.api_llm_available_models = api.get_available_models()
        logger.info(f"Available LLM Models: {len(self.api_llm_available_models)}")
        self.local_llm_available_models = {}
        for model in self.api_llm_available_models:
            self.local_llm_available_models[model["model_name"]] = (
                QuantizationLLMModelConfig(**model)
            )

    def handle_task(self, task: Task):
        """
        Handle the task
        Args:
            task (Task): The task to handle

        Returns:

        """
        TimeLogger.log_task(task, "start_quantization_llm")
        result_profile = {}
        latency_profile = {}
        quantization_llm_parameters = QuantizationLLMParameters(**task.parameters)
        text = quantization_llm_parameters.text
        llm_model_name = quantization_llm_parameters.llm_model_name
        # get llm_model
        llm_model = self.local_llm_available_models.get(llm_model_name, None)
        if llm_model is None:
            logger.error(f"Model {llm_model_name} not found")
            task.result_status = ResultStatus.failed.value
            task.description = f"Model {llm_model_name} not found"
            return task

        if llm_model.llm is None:
            logger.error(f"Model {llm_model_name} not loaded")
            try:
                with time_tracker(
                    "init_llm", latency_profile, track_type=TrackType.MODEL.value
                ):
                    llm_model.init_llm()
            except Exception as llm_err:
                logger.exception(llm_err)
                task.result_status = ResultStatus.failed.value
                task.description = str(llm_err)
                return task
        with time_tracker("infer", latency_profile, track_type=TrackType.MODEL.value):
            logger.info(f"Text: {text}")
            res_text, logs = self.infer(
                text=text,
                llm_model_config=llm_model,
            )
        result_profile["logs"] = logs
        result_profile["text"] = res_text
        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        TimeLogger.log_task(task, "end_quantization_llm")
        return task

    @staticmethod
    def infer(text: str, llm_model_config: QuantizationLLMModelConfig):
        """
        Infer the task
        Args:
            text (str): The text to infer
            llm_model_config (QuantizationLLMModelConfig): The llm model config

        Returns:

        """
        llm_adaptor = QuantizationLLMAdaptor(llm_model_config)
        res = llm_adaptor.create_chat_completion(
            prompt=text,
        )
        logger.info(res)
        text = res["choices"][0]["message"]["content"]

        return text, res
