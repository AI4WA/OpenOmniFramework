from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from authenticate.utils.get_logger import get_logger
from llm.admin import LLMRequestRecordResource
from llm.models import LLMRequestRecord

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Check or download models"

    def add_arguments(self, parser):
        """
        Add arguments to the command
        """
        parser.add_argument(
            "--task_name",
            type=str,
            help="The name of the model to check or download, if it is all, then download all",
            default="llama2-7b-chat",
        )

    def handle(self, *args, **options):
        """
        Loop through the MODELS dictionary and check if the model is in the database. If it is not, add it.
        :param args:
        :param options:
        :return:
        """
        task_name = options["task_name"]
        self.export_to_csv(task_name=task_name)

    @classmethod
    def export_to_csv(cls, task_name: str = None):
        if task_name is None:
            logger.error("Task Name is required")
            return
        resource = LLMRequestRecordResource()
        dataset = resource.export(
            queryset=LLMRequestRecord.objects.filter(name=task_name, success=True)
        )
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(
            f"{settings.TMP_FOLDER}/{task_name}_{current_datetime}.csv", "wb"
        ) as file:
            file.write(dataset.csv.encode())
        logger.info(f"Exported {task_name} to csv file")
        logger.info(
            f"File path: {settings.TMP_FOLDER}/{task_name}_{current_datetime}.csv"
        )
