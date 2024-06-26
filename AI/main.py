import argparse
import os
import time
import uuid
from typing import Optional

# load env from file
from dotenv import load_dotenv

from models.task import Task
from modules.emotion_detection.handler import EmotionDetectionHandler
from modules.hf_llm.handler import HFLLM
from modules.quantization_llm.handler import QuantizationLLM
from modules.speech_to_text.speech2text import Speech2Text
from modules.text_to_speech.text2speech import Text2Speech
from utils.api import API
from utils.constants import API_DOMAIN
from utils.get_logger import get_logger
from utils.timer import timer

logger = get_logger("AI-Worker")


class AIOrchestrator:
    """
    This is the AI Orchestrator

    We will pull the task from the API end
    And then based on which type of the task it is, we will send it to the respective handler
    """

    def __init__(
        self,
        api_domain: str,
        token: str,
        task_name: Optional[str] = "all",
        time_sleep: Optional[float] = 1.5,
    ):
        """
        Initialize the AI Orchestrator
        Args:
            api_domain (str): The API Domain
            token (str): The API Token
            task_name (str): The task name. Default is "all"
            time_sleep (float): The time to sleep. Default is 1.5 during each loop
        """
        self.uuid = str(uuid.uuid4())
        self.api_domain = api_domain
        self.token = token
        self.task_name = task_name
        self.api = API(
            domain=api_domain, token=token, task_name=task_name, uuid=self.uuid
        )
        self.api.register_or_update_worker()

        # controller
        self.counter = 0
        self.time_sleep = time_sleep

        # first check the authentication of the token valid or not
        if not self.authenticate_token():
            raise Exception("Token is not valid")

        if not self.pre_env_check():
            raise Exception("Pre Environment Check Failed")

        self.speech2text = None
        self.text2speech = None
        self.emotion_detection = None
        self.quantization_llm = None
        self.hf_llm = None

        self.task_name_router = {
            "speech2text": self.handle_speech2text_task,
            "text2speech": self.handle_text2speech_task,
            "emotion_detection": self.handle_emotion_detection_task,
            "quantization_llm": self.handle_quantization_llm_task,
            "hf_llm": self.handle_hf_llm_task,
        }

    def authenticate_token(self):
        """
        Authenticate the token
        Returns:
            bool: True if the token is valid
        """
        return self.api.verify_token()

    def pre_env_check(self):
        # if task is text 2 speech, check openai key
        load_dotenv()
        if self.task_name in ["all", "text2speech"]:
            # check openai key
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key is None:
                # READ from .env, and set it
                # if it not exists, then return False
                logger.error("OpenAI API Key is not set")
                return False
        if self.task_name in ["all", "hf_llm"]:
            # check openai key
            openai_key = os.getenv("HF_TOKEN")
            if openai_key is None:
                logger.error("OpenAI HF TOKEN is not set")
                return False
        return True

    def run(self):
        logger.info(f"AI Worker Running UUID: {self.uuid}")
        while True:
            self.counter += 1
            if self.counter % 50 == 0:
                # report to the cloud that we are still alive
                logger.info(f"Still alive. Counter: {self.counter}")
                self.api.register_or_update_worker()
            try:
                with timer(logger=logger, message="get_task"):
                    task = self.api.get_task()
                # after get the task, then feed it to the model to evaluate the model params
                if task is None:
                    logger.info("No task found")
                    time.sleep(self.time_sleep)
                    continue
                self.handle_task(task)
            # allow it accepts keyboard interrupt
            except KeyboardInterrupt:
                logger.info("Keyboard Interrupt")
                break
            except Exception as e:
                logger.exception(e)
            time.sleep(self.time_sleep)

    def handle_task(self, task: dict):
        """
        Handle the task
        Args:
            task (dict): The task
        """
        task_obj = Task(**task)
        logger.info(task_obj)
        if task_obj.task_name in self.task_name_router:
            task_obj = self.task_name_router[task_obj.task_name](task_obj)
        else:
            logger.error(f"Unknown task type: {task_obj.task_name}")
            task_obj.result_status = "failed"
            task_obj.result_json = {"error": f"Unknown task type: {task_obj.task_name}"}

        # then update the task status
        self.api.post_task_result(task_obj)

    def handle_speech2text_task(self, task: Task):
        """
        Handle the speech2text task
        Args:
            task (Task): The task
        """
        if self.speech2text is None:
            self.speech2text = Speech2Text()
        task = self.speech2text.handle_task(task)
        return task

    def handle_text2speech_task(self, task: Task):
        """
        Handle the text2speech task
        Args:
            task (Task): The task
        """
        if self.text2speech is None:
            self.text2speech = Text2Speech()
        task = self.text2speech.handle_task(task)
        return task

    def handle_emotion_detection_task(self, task: Task):
        """
        Handle the emotion detection task
        Args:
            task (Task): The task
        """
        if self.emotion_detection is None:
            self.emotion_detection = EmotionDetectionHandler()
        task = self.emotion_detection.handle_task(task)
        return task

    def handle_quantization_llm_task(self, task: Task):
        """
        Handle the quantization llm task
        Args:
            task (Task): The task
        """
        if self.quantization_llm is None:
            self.quantization_llm = QuantizationLLM(api=self.api)
        task = self.quantization_llm.handle_task(task)
        return task

    def handle_hf_llm_task(self, task: Task):
        """
        Handle the hf llm task which will require more time compare to other tasks
        Args:
            task (Task): The task

        Returns:

        """
        if self.hf_llm is None:
            self.hf_llm = HFLLM()
        task = self.hf_llm.handle_task(task)
        return task


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args.add_argument("--task_name", type=str, required=False, default="all")
    args = args.parse_args()

    ai_orchestrator = AIOrchestrator(
        api_domain=args.api_domain, token=args.token, task_name=args.task_name
    )
    ai_orchestrator.run()
