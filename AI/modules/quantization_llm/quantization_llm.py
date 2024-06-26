from datetime import datetime

from models.parameters import QuantizationLLMParameters
from models.task import Task
from modules.quantization_llm.models import QuantizationLLMModelConfig
from utils.api import API
from utils.get_logger import get_logger

from .adaptor_worker import QuantizationLLMAdaptor

logger = get_logger(__name__)

#
# class LlamaMessage(BaseModel):
#     role: str
#     content: str
#
#
# class LlamaParams(BaseModel):
#     llm_model_name: str
#     llm_task_type: str
#     prompt: str = None
#     messages: List[LlamaMessage] = None
#
#
# class LLMTask:
#     def __init__(self, name: str, parameters: LlamaParams, *args, **kwargs):
#         self.task_id = kwargs.get("id")
#         self.name = name
#         self.parameters = parameters
#         self.llm_model_name = parameters.get("model_name")
#         self.llm_task_type = parameters.get("llm_task_type")
#         self.llm_prompt = parameters.get("prompt")
#         self.llm_messages = parameters.get("messages", None)
#         self.llm_tools = parameters.get("tools", None)
#         self.llm_tool_choice = parameters.get("tool_choice", None)
#         logger.debug(args)
#         logger.debug(kwargs)
#
#     def run(self, model_config):
#         llm_adaptor = QuantizationLLMAdaptor(model_config)
#         if self.llm_task_type == "chat_completion":
#             return llm_adaptor.create_chat_completion(
#                 prompt=self.llm_prompt,
#                 messages=self.llm_messages,
#                 tools=self.llm_tools,
#                 tool_choice=self.llm_tool_choice,
#             )
#         elif self.llm_task_type == "completion":
#             return llm_adaptor.create_completion(self.llm_prompt)
#         elif self.llm_task_type == "create_embedding":
#             return llm_adaptor.create_embedding(self.llm_prompt)
#         else:
#             raise ValueError(f"Invalid LLM task type: {self.llm_task_type}")
#


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
        result_profile = {}
        latency_profile = {}
        quantization_llm_parameters = QuantizationLLMParameters(**task.parameters)
        prompt = quantization_llm_parameters.prompt
        llm_model_name = quantization_llm_parameters.llm_model_name
        # get llm_model
        llm_model = self.local_llm_available_models.get(llm_model_name, None)
        if llm_model is None:
            logger.error(f"Model {llm_model_name} not found")
            task.result_status = "failed"
            task.description = f"Model {llm_model_name} not found"
            return task

        if llm_model.llm is None:
            logger.error(f"Model {llm_model_name} not loaded")
            try:
                start_time = datetime.now()
                llm_model.init_llm()
                end_time = datetime.now()
                latency_profile["model_init_llm"] = (
                    end_time - start_time
                ).total_seconds()
            except Exception as llm_err:
                logger.exception(llm_err)
                task.result_status = "failed"
                task.description = str(llm_err)
                return task
        start_time = datetime.now()
        logger.info(f"Text: {prompt}")
        res_text, logs = self.infer(
            text=prompt,
            llm_model_config=llm_model,
        )
        latency_profile["model_infer"] = (datetime.now() - start_time).total_seconds()
        result_profile["logs"] = logs
        result_profile["text"] = res_text
        task.result_status = "completed"
        task.result_json["result_profile"] = result_profile
        task.result_json["latency_profile"] = latency_profile

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
