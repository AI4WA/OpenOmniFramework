from typing import List

from pydantic import BaseModel

from utils.get_logger import get_logger

from .adaptor_worker import QuantizationLLMAdaptor

logger = get_logger(__name__)


class LlamaMessage(BaseModel):
    role: str
    content: str


class LlamaParams(BaseModel):
    llm_model_name: str
    llm_task_type: str
    prompt: str = None
    messages: List[LlamaMessage] = None


class LLMTask:
    def __init__(self, name: str, parameters: LlamaParams, *args, **kwargs):
        self.task_id = kwargs.get("id")
        self.name = name
        self.parameters = parameters
        self.llm_model_name = parameters.get("model_name")
        self.llm_task_type = parameters.get("llm_task_type")
        self.llm_prompt = parameters.get("prompt")
        self.llm_messages = parameters.get("messages", None)
        self.llm_tools = parameters.get("tools", None)
        self.llm_tool_choice = parameters.get("tool_choice", None)
        logger.debug(args)
        logger.debug(kwargs)

    def run(self, model_config):
        llm_adaptor = QuantizationLLMAdaptor(model_config)
        if self.llm_task_type == "chat_completion":
            return llm_adaptor.create_chat_completion(
                prompt=self.llm_prompt,
                messages=self.llm_messages,
                tools=self.llm_tools,
                tool_choice=self.llm_tool_choice,
            )
        elif self.llm_task_type == "completion":
            return llm_adaptor.create_completion(self.llm_prompt)
        elif self.llm_task_type == "create_embedding":
            return llm_adaptor.create_embedding(self.llm_prompt)
        else:
            raise ValueError(f"Invalid LLM task type: {self.llm_task_type}")
