import time

from django.core.management import call_command
from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from worker.models import Task
from worker.translator import Translator

logger = get_logger(__name__)

LISTEN_TO_TASKS = ["stt", "cmc"]


class Command(BaseCommand):
    help = "Run the worker to finish the cmc or stt tasks."

    def handle(self, *args, **options):
        """
        Handle the command
        Loop through all tasks and check if they are completed

        """

        logger.info("Running worker for stt and cmc")
        translator = Translator()

        while True:
            tasks = Task.objects.filter(
                result_status="pending", work_type__in=LISTEN_TO_TASKS
            )
            for task in tasks:
                task.result_status = "started"
                task.save()
                if task.work_type == "stt":
                    self.run_stt_task(translator, task)
                elif task.work_type == "cmc":
                    self.run_cmc_task(task)
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

    @staticmethod
    def run_cmc_task(task):
        logger.info("Running call management command task")
        """
        Run a call management command task
        """
        try:
            params = task.parameters
            options = params.get("options", {})
            command = params.get("command", "")
            call_command(command, **options)
            task.result_status = "completed"
            task.save()
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            task.result_status = "failed"
            task.description = str(e)
            task.save()
