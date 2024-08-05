import argparse
import os
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from typing import Optional

# load env from file
from dotenv import load_dotenv

from models.task import ResultStatus, Task, TaskName
from modules.emotion_detection.handler import EmotionDetectionHandler
from modules.general_ml.handler import GeneralMLModel
from modules.hf_llm.handler import HFLLM
from modules.openai.handler import OpenAIHandler
from modules.quantization_llm.handler import QuantizationLLM
from modules.rag.handler import RAGHandler
from modules.speech_to_text.speech2text import Speech2Text
from modules.text_to_speech.text2speech import Text2Speech
from utils.api import API
from utils.constants import API_DOMAIN
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
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
        self.storage_solution = self.api.get_storage_solution()
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
        self.general_ml = None
        self.openai_handler = None
        self.rag_handler = None

        self.task_name_router = {
            TaskName.speech2text.value: self.handle_speech2text_task,
            TaskName.text2speech.value: self.handle_text2speech_task,
            TaskName.emotion_detection.value: self.handle_emotion_detection_task,
            TaskName.quantization_llm.value: self.handle_quantization_llm_task,
            TaskName.hf_llm.value: self.handle_hf_llm_task,
            TaskName.general_ml.value: self.handle_general_ml_task,
            TaskName.openai_gpt4o.value: self.handle_openai_task,
            TaskName.openai_speech2text.value: self.handle_openai_task,
            TaskName.openai_text2speech.value: self.handle_openai_task,
            TaskName.openai_gpt4o_text_only.value: self.handle_openai_task,
            TaskName.openai_gpt_4o_text_and_image.value: self.handle_openai_task,
            TaskName.rag.value: self.handle_rag_task,
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
        TimeLogger.log_task(task_obj, "start_task")
        if task_obj.task_name in self.task_name_router:
            task_obj = self.task_name_router[task_obj.task_name](task_obj)
        elif "openai" in task_obj.task_name:
            task_obj = self.handle_openai_task(task_obj)
        else:
            logger.error(f"Unknown task type: {task_obj.task_name}")
            task_obj.result_status = ResultStatus.failed.value
            task_obj.description = f"Unknown task type: {task_obj.task_name}"
        TimeLogger.log_task(task_obj, "end_task")
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

    def handle_general_ml_task(self, task: Task):
        """
        Handle the general ml task
        Args:
            task (Task): The task

        Returns:

        """
        if self.general_ml is None:
            self.general_ml = GeneralMLModel()
        task = self.general_ml.handle_task(task)
        return task

    def handle_openai_task(self, task: Task):
        """
        Handle the openai task
        Args:
            task (Task): The task

        Returns:

        """
        if self.openai_handler is None:
            self.openai_handler = OpenAIHandler()
        task = self.openai_handler.handle_task(task)
        return task

    def handle_rag_task(self, task: Task):
        """
        Handle the rag task
        Args:
            task (Task): The task

        Returns:

        """
        if self.rag_handler is None:
            self.rag_handler = RAGHandler()
        task = self.rag_handler.handle_task(task)
        return task


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--token", type=str, required=True)
    args.add_argument("--api_domain", type=str, required=False, default=API_DOMAIN)
    args.add_argument("--task_name", type=str, required=False, default="all")
    args.add_argument("--multi_processing", type=int, required=False, default=0)
    args = args.parse_args()

    if args.multi_processing == 0:
        ai_orchestrator = AIOrchestrator(
            api_domain=args.api_domain, token=args.token, task_name=args.task_name
        )
        ai_orchestrator.run()
    else:
        if "all" in args.task_name:
            task_names = [
                TaskName.quantization_llm.value,
                TaskName.hf_llm.value,
                TaskName.emotion_detection.value,
                TaskName.general_ml.value,
                TaskName.openai_gpt4o.value,
                TaskName.openai_speech2text.value,
                TaskName.openai_text2speech.value,
                TaskName.speech2text.value,
                TaskName.text2speech.value,
                TaskName.openai_gpt4o_text_only.value,
                TaskName.openai_gpt_4o_text_and_image.value,
                TaskName.rag.value,
            ]
        else:
            task_names = args.task_name.split(",")

        # get multiple processes to run the ai_orchestrator
        with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
            futures = []
            for task_name in task_names:
                futures.append(
                    executor.submit(
                        AIOrchestrator(
                            api_domain=args.api_domain,
                            token=args.token,
                            task_name=task_name,
                        ).run
                    )
                )
            for future in futures:
                future.result()
