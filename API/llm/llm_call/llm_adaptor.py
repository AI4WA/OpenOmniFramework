from llama_cpp import Llama
from django.conf import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LLMAdaptor:
    def __init__(self, model_name: str):
        logger.info(f"Creating LLMAdaptor for model {model_name}")
        self.model_name = model_name

    @staticmethod
    def get_llama_2():
        model_path = Path(settings.BASE_DIR / "llm" / "llm_call" / "models" / "llama-2-13b-chat.Q8_0.gguf")
        if not model_path.exists():
            raise ValueError(f"Model {model_path} does not exist")
        return Llama(model_path=model_path.as_posix())

    @staticmethod
    def get_gemma():
        model_path = Path(settings.BASE_DIR / "llm" / "llm_call" / "models" / "gemma-7b-it.gguf")
        if not model_path.exists():
            raise ValueError(f"Model {model_path} does not exist")
        return Llama(model_path=model_path.as_posix())

    def get_response(self, prompt: str):
        logger.info(f"Getting response for prompt: {prompt}")
        if self.model_name == "llama2":
            llm = self.get_llama_2()
        elif self.model_name == "gemma":
            llm = self.get_gemma()
        else:
            raise ValueError(f"Model {self.model_name} is not supported")
        output = llm(
            f"Q: {prompt} A: ",
            max_tokens=500,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stop=["Q:", "\n"],  # Stop generating just before the model would generate a new question
            echo=True  # Echo the prompt back in the output
        )
        logger.info(f"Response: {output}")
        return output
