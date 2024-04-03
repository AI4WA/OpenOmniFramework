from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

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
        parser.add_argument(
            "--rows_per_csv",
            type=int,
            help="The number of rows per csv file",
            default=20000,
        )

    def handle(self, *args, **options):
        """
        Loop through the MODELS dictionary and check if the model is in the database. If it is not, add it.
        :param args:
        :param options:
        :return:
        """
        task_name = options["task_name"]
        rows_per_csv = options["rows_per_csv"]
        self.export_to_csv(task_name=task_name, rows_per_csv=rows_per_csv)

    @classmethod
    def export_to_csv(cls, task_name: str = None, rows_per_csv: int = 20000):
        if task_name is None:
            logger.error("Task Name is required")
            return

        # limit the queryset to the number of rows per csv file
        queryset = LLMRequestRecord.objects.filter(name=task_name, success=True)
        if not queryset.exists():
            logger.error(f"No records found for task_name: {task_name}")
            return

        paginator = Paginator(queryset, rows_per_csv)

        for page_num in range(1, paginator.num_pages + 1):
            page = paginator.page(page_num)
            resource = LLMRequestRecordResource()
            dataset = resource.export(page.object_list)

            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{settings.TMP_FOLDER}/{task_name}_{current_datetime}_part{page_num}.csv"

            with open(filename, "wb") as file:
                file.write(dataset.csv.encode())

            logger.info(f"Exported {task_name} part {page_num} to csv file")
            logger.info(f"File path: {filename}")
