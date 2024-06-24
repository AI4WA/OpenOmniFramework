from typing import Dict, List

import chatglm_cpp
from llama_cpp.llama_types import ChatCompletionTool, ChatCompletionToolChoiceOption

from constants import HF_LLAMA, MT_CHATGLM, MT_LLAMA
from llm_models import LLMModelConfig
from utils import get_logger

logger = get_logger(__name__)


class LLMAdaptor:
    def __init__(self, model_config: LLMModelConfig):
        self.model_config = model_config
        self.model_path = model_config.model_path()
        self.llm = self.model_config.llm

    def create_completion(self, prompt: str):
        """
        Create a completion for the given prompt
        :param prompt:
        :return:
        """

        if self.model_config.model_type in [MT_LLAMA, HF_LLAMA]:
            output = self.llm(
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

    def create_chat_completion(
        self,
        prompt: str = None,
        messages: List[Dict[str, str]] = None,
        tools: List[ChatCompletionTool] = None,
        tool_choice: ChatCompletionToolChoiceOption = None,
        handle_chat: bool = False,
        *args,
        **kwargs,
    ):
        if messages:
            """
            This is trying to replicate passing all params chat completion provided via llama_cpp
            """
            if self.model_config.model_type == HF_LLAMA:
                logger.info(f"Creating chat completion for messages: {messages}")
                construct_prompt = self.llm.tokenizer.apply_chat_template(
                    conversation=messages, tokenize=False, add_generation_prompt=True
                )
                terminators = [
                    self.llm.tokenizer.eos_token_id,
                    self.llm.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
                ]
                res = self.llm(
                    construct_prompt,
                    max_new_tokens=256,
                    eos_token_id=terminators,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )
                if handle_chat:
                    return res[0]["generated_text"][len(construct_prompt) :]
                return res
            if self.model_config.model_type == MT_LLAMA:
                logger.info(f"Creating chat completion for messages: {messages}")
                return self.llm.create_chat_completion(
                    messages=messages, tools=tools, tool_choice=tool_choice
                )
            raise ValueError(
                f"Model {self.model_config.model_type} is not supported when messages are provided"
            )

        if prompt:
            """
            Simple version of it, without message "role" definition
            """
            if self.model_config.model_type == HF_LLAMA:
                if handle_chat:
                    return self.llm(prompt)[0]["generated_text"][len(prompt) :]
                return self.llm(prompt)
            if self.model_config.model_type == MT_LLAMA:
                res = self.llm.create_chat_completion(
                    messages=[
                        {"role": "user", "content": prompt},
                    ]
                )
                if handle_chat:
                    return res["choices"][0]["message"]["content"]
                return res
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
        raise ValueError("Prompt or messages are required")

    def create_embedding(self, text: str):
        if text is None:
            raise ValueError("Text is required")
        if self.model_config.model_type == MT_LLAMA:
            logger.info(f"Creating embedding for text: {text}")
            return self.llm.create_embedding(text)
        raise ValueError(
            f"Model {self.model_config.model_type} is not supported for embedding"
        )
