import logging

from django.core.management.base import BaseCommand
import time
from django.conf import settings
from worker.models import Task
from llm.llm_call.llm_adaptor import LLMAdaptor
from worker.translator import Translator
from llm.models import LLMRequestRecord

from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Run the worker to finish the llm or stt tasks.'

    def add_arguments(self, parser):
        """
        Add arguments to the command
        """
        parser.add_argument('--task_type', type=str, help='The type of task to run', default='llm')

    def handle(self, *args, **options):
        """
        Handle the command
        Loop through all tasks and check if they are completed

        """
        task_type = options['task_type']
        if task_type == "stt":
            logger.info("Running STT worker...")
            translator = Translator()
        else:
            translator = None
        while True:
            tasks = Task.objects.filter(result_status='pending', work_type=task_type)
            for task in tasks:
                task.result_status = 'started'
                task.save()
                if task.work_type == 'llm':
                    self.run_llm_task(task)
                elif task.work_type == 'stt':
                    self.run_stt_task(translator, task)
                else:
                    logger.error(f"Unknown task type: {task.work_type}")
            logger.info("Worker running...")
            time.sleep(5)

    @staticmethod
    def run_llm_task(task):
        """
        Run a LLM task
        """
        params = task.parameters
        model_name = params.get('model_name', None)
        if model_name is None:
            task.result_status = 'failed'
            task.save()
            logger.error(f"Task {task.id} failed because model_name is not provided")
            return

        prompt = params.get('prompt', None)
        if prompt is None:
            task.result_status = 'failed'
            task.save()
            logger.error(f"Task {task.id} failed because prompt is not provided")
            return
        llm_task_type = params.get('llm_task_type', 'chat_completion')
        start_time = time.time()
        try:
            adaptor = LLMAdaptor(model_name)
            if llm_task_type == 'chat_completion':
                response = adaptor.create_chat_completion(prompt)
            elif llm_task_type == 'completion':
                response = adaptor.create_completion(prompt)
            elif llm_task_type == 'create_embedding':
                response = adaptor.create_embedding(prompt)
            else:
                raise Exception(f"Unknown llm task type: {llm_task_type}")
            end_time = time.time()
            record = LLMRequestRecord(
                user=task.user,
                model_name=model_name,
                prompt=prompt,
                response=response,
                task="chat-completion",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            task.result_status = 'completed'
            task.description = str(response)
            task.save()
            logger.info(response)
            logger.info(f"Task {task.id} completed in {end_time - start_time} seconds")
        except Exception as e:
            logger.error(e)
            end_time = time.time()
            task.result_status = 'failed'
            task.description = str(e)
            task.save()
            logger.error(f"Task {task.id} failed in {end_time - start_time} seconds")
            logger.error(e)

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
