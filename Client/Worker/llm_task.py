from llm_adaptor_worker import LLMAdaptor
from utils import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class LlamaMessage(BaseModel):
    role: str
    content: str


class LlamaParams(BaseModel):
    model_name: str
    llm_task_type: str
    prompt: str = None
    messages: list[LlamaMessage] = None


class LLMTask:
    def __init__(self, name: str, parameters: LlamaParams, *args, **kwargs):
        self.task_id = kwargs.get("id")
        self.name = name
        self.parameters = parameters
        self.llm_model_name = parameters.get("model_name")
        self.llm_task_type = parameters.get("llm_task_type")
        self.llm_prompt = parameters.get("prompt")
        logger.debug(args)
        logger.debug(kwargs)

    def run(self, model_config):
        llm_adaptor = LLMAdaptor(model_config)
        if self.llm_task_type == "chat_completion":
            return llm_adaptor.create_chat_completion(self.llm_prompt)
        elif self.llm_task_type == "completion":
            return llm_adaptor.create_completion(self.llm_prompt)
        elif self.llm_task_type == "create_embedding":
            return llm_adaptor.create_embedding(self.llm_prompt)
        else:
            raise ValueError(f"Invalid LLM task type: {self.llm_task_type}")
