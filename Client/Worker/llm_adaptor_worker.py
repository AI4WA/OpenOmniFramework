from utils import get_logger
from constants import MT_LLAMA, MT_CHATGLM
import chatglm_cpp
from llama_cpp import Llama
from llm_models import LLMModelConfig
from pathlib import Path

logger = get_logger(__name__)


class LLMAdaptor:
    def __init__(self, model_config: LLMModelConfig):
        self.model_config = model_config
        self.model_path = model_config.model_path()

    def create_completion(self, prompt: str):
        """
        Create a completion for the given prompt
        :param prompt:
        :return:
        """

        if self.model_config.model_type == MT_LLAMA:
            llm = Llama(
                model_path=self.model_path.as_posix(), n_gpu_layers=-1, embedding=False
            )

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
        if self.model_config.model_type == MT_CHATGLM:
            chatglm_pipeline = chatglm_cpp.Pipeline(
                model_path=self.model_path.as_posix()
            )
            output = chatglm_pipeline.generate(prompt)
            logger.critical(f"Response: {output}")
            return {"content": output}
        raise ValueError(f"Model {self.model_config.model_type} is not supported")

    def create_chat_completion(self, prompt: str):
        if self.model_config.model_type == MT_LLAMA:
            llm = Llama(
                model_path=self.model_path.as_posix(), n_gpu_layers=-1, embedding=False
            )

            return llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant who perfectly understand Western Australia.",
                    },
                    {"role": "user", "content": prompt},
                ]
            )
        if self.model_config.model_type == MT_CHATGLM:
            chatglm_pipeline = chatglm_cpp.Pipeline(
                model_path=self.model_path.as_posix()
            )
            output = chatglm_pipeline.chat(
                [chatglm_cpp.ChatMessage(role="user", content=prompt)]
            )
            logger.critical(f"Response: {output}")
            return {"role": output.role, "content": output.content}
        raise ValueError(f"Model {self.model_config.model_type} is not supported")

    def create_embedding(self, text: str):
        if self.model_config.model_type == MT_LLAMA:
            llm = Llama(
                model_path=self.model_path.as_posix(), n_gpu_layers=-1, embedding=True
            )
            return llm.create_embedding(text)
        raise ValueError(
            f"Model {self.model_config.model_type} is not supported for embedding"
        )
