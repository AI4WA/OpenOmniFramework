import time

from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from llm.models import LLMRequestRecord
from worker.models import Task
from worker.translator import Translator

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run the worker to finish the llm or stt tasks."

    def add_arguments(self, parser):
        """
        Add arguments to the command
        """
        parser.add_argument(
            "--task_type", type=str, help="The type of task to run", default="llm"
        )

    def handle(self, *args, **options):
        """
        Handle the command
        Loop through all tasks and check if they are completed

        """
        task_type = options["task_type"]
        if task_type == "stt":
            logger.info("Running STT worker...")
            translator = Translator()
        else:
            translator = None
        while True:
            tasks = Task.objects.filter(result_status="pending", work_type=task_type)
            for task in tasks:
                task.result_status = "started"
                task.save()
                if task.work_type == "stt":
                    self.run_stt_task(translator, task)
                else:
                    logger.error(f"Unknown task type: {task.work_type}")
            logger.info("Worker running...")
            time.sleep(5)

    @staticmethod
    def run_stt_task(translator, task):
        """
        Run task to get the text from an audio file work
        1. Device will sync the audio file to the home server
        2. We will need to mount the data folder to the worker container
        3. And then triggered by a signal to do the detection (normally by the client end API call)
        4. Write it to the database
        """

        translator.handle_task(task)
