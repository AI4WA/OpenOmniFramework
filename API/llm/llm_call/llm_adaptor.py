import logging
from pathlib import Path

import chatglm_cpp
from django.conf import settings
from llama_cpp import Llama

from llm.llm_call.config import MN_GEMMA, MN_LLAMA2, MODELS, MT_CHATGLM, MT_LLAMA
from llm.models import LLMConfigRecords

logger = logging.getLogger(__name__)


class LLMAdaptor:
    def __init__(self, model_name: str):
        logger.info(f"Creating LLMAdaptor for model {model_name}")
        self.model_name = model_name

    def get_llm_model_config(self):
        """

        :return:
        """

        model_config = LLMConfigRecords.objects.filter(
            model_name=self.model_name
        ).first()
        if model_config is None:
            raise ValueError(f"Model {self.model_name} is not supported")

        model_path = Path(
            settings.BASE_DIR
            / "llm"
            / "llm_call"
            / "models"
            / model_config.model_family
            / model_config.filename
        )
        if not model_path.exists():
            logger.info(f"Model {model_path} does not exist, downloading")
            raise ValueError(f"Model {self.model_name} is not supported")
        logger.info(f"Creating LLM client for model {model_path}")
        return model_config

    def create_completion(self, prompt: str):
        """
        Create a completion for the given prompt
        :param prompt:
        :return:
        """
        model_config = self.get_llm_model_config()
        if model_config.model_type == MT_LLAMA:
            model_path = Path(
                settings.BASE_DIR
                / "llm"
                / "llm_call"
                / "models"
                / model_config.model_family
                / model_config.filename
            )
            llm = Llama(model_path=model_path.as_posix(), embedding=False)

            output = llm(
                f"Q: {prompt} A: ",
                max_tokens=500,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
                stop=[
                    "Q:",
                    "\n",
                ],  # Stop generating just before the model would generate a new question
                echo=True,  # Echo the prompt back in the output
            )
            logger.info(f"Response: {output}")
            return output
        if model_config.model_type == MT_CHATGLM:
            model_path = Path(
                settings.BASE_DIR
                / "llm"
                / "llm_call"
                / "models"
                / model_config.model_family
                / model_config.filename
            )
            chatglm_pipeline = chatglm_cpp.Pipeline(model_path=model_path.as_posix())
            output = chatglm_pipeline.generate(prompt)
            logger.critical(f"Response: {output}")
            return {"content": output}
        raise ValueError(f"Model {model_config.model_type} is not supported")

    def create_chat_completion(self, prompt: str):
        model_config = self.get_llm_model_config()
        if model_config.model_type == MT_LLAMA:
            model_path = Path(
                settings.BASE_DIR
                / "llm"
                / "llm_call"
                / "models"
                / model_config.model_family
                / model_config.filename
            )
            llm = Llama(model_path=model_path.as_posix(), embedding=False)

            return llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant who perfectly understand Western Australia.",
                    },
                    {"role": "user", "content": prompt},
                ]
            )
        if model_config.model_type == MT_CHATGLM:
            model_path = Path(
                settings.BASE_DIR
                / "llm"
                / "llm_call"
                / "models"
                / model_config.model_family
                / model_config.filename
            )
            chatglm_pipeline = chatglm_cpp.Pipeline(model_path=model_path.as_posix())
            output = chatglm_pipeline.chat(
                [chatglm_cpp.ChatMessage(role="user", content=prompt)]
            )
            logger.critical(f"Response: {output}")
            return {"role": output.role, "content": output.content}
        raise ValueError(f"Model {model_config.model_type} is not supported")

    def create_embedding(self, text: str):
        model_config = self.get_llm_model_config()
        if model_config.model_type == MT_LLAMA:
            model_path = Path(
                settings.BASE_DIR
                / "llm"
                / "llm_call"
                / "models"
                / model_config.model_family
                / model_config.filename
            )
            llm = Llama(model_path=model_path.as_posix(), embedding=True)
            return llm.create_embedding(text)
        raise ValueError(
            f"Model {model_config.model_type} is not supported for embedding"
        )
