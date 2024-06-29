from openai import OpenAI
from utils.get_logger import get_logger

logger = get_logger(__name__)
client = OpenAI()


class OpenAIHandler:
    def __init__(self):
        self.client = OpenAI()

    def speech2text(self, prompt: str):
        """
        Call OpenAI endpoints to convert speech to text
        Args:
            prompt (str): The prompt

        Returns:

        """
        logger.info(f"Getting response for the prompt: {prompt}")
