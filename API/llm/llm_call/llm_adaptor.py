from llama_cpp import Llama
from django.conf import settings
from pathlib import Path
import logging
from llm.llm_call.config import MT_LLAMA, MODELS, MN_LLAMA2, MN_GEMMA
from huggingface_hub import hf_hub_url

logger = logging.getLogger(__name__)


class LLMAdaptor:
    def __init__(self, model_name: str):
        logger.info(f"Creating LLMAdaptor for model {model_name}")
        self.model_name = model_name

    def get_llm_client(self):
        general_model_name = self.model_name.split("-")[0]
        model_details = None
        model_type = None
        for model in MODELS:
            if model["name"] == general_model_name:
                model_type = model["model_type"]
                for the_model in model["models"]:
                    if the_model["name"] == self.model_name:
                        model_details = the_model
                        break
                break
        if model_details is None:
            raise ValueError(f"Model {self.model_name} is not supported")
        model_path = Path(
            settings.BASE_DIR / "llm" / "llm_call" / "models" / general_model_name / model_details["filename"])
        if not model_path.exists():
            self.download_model(model_details)
            raise ValueError(f"Model {model_path} does not exist")
        logger.info(f"Creating LLM client for model {model_path}")
        if model_type == MT_LLAMA:
            return Llama(model_path=model_path.as_posix())
        raise ValueError(f"Model type {model_type} is not supported")

    @staticmethod
    def download_model(model_details: dict):
        """
        Download the model from the model_details
        :param model_details:
        :return:
        """
        download_url = hf_hub_url(repo_id=model_details["repo"], filename=model_details["filename"])
        logger.critical(f"Downloading model from {download_url}")

    def get_prompt(self):
        """
        From the history of the conversation, get the prompt to be used for the next response
        :return:
        """
        pass

    def get_response(self, prompt: str):
        llm = self.get_llm_client()
        output = llm(
            f"Q: {prompt} A: ",
            max_tokens=500,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stop=["Q:", "\n"],  # Stop generating just before the model would generate a new question
            echo=True  # Echo the prompt back in the output
        )
        logger.info(f"Response: {output}")
        return output
