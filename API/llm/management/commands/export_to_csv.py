import os
import zipfile
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from authenticate.utils.get_logger import get_logger
from llm.admin import LLMRequestRecordResource
from llm.models import LLMRequestRecord, LLMRequestResultDownload

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

        parser.add_argument(
            "--user_id",
            type=int,
            help="The user id",
            default=None,
        )
        parser.add_argument("--task_id", type=int, help="The task id", default=None)

    def handle(self, *args, **options):
        """
        Loop through the MODELS dictionary and check if the model is in the database. If it is not, add it.
        :param args:
        :param options:
        :return:
        """
        task_name = options["task_name"]
        rows_per_csv = options["rows_per_csv"]
        user_id = options["user_id"]
        task_id = options["task_id"]
        self.export_to_csv(
            task_name=task_name,
            rows_per_csv=rows_per_csv,
            user_id=user_id,
            task_id=task_id,
        )

    @classmethod
    def export_to_csv(
        cls,
        task_name: str = None,
        rows_per_csv: int = 20000,
        user_id: int = None,
        task_id: int = None,
    ):
        if task_name is None:
            logger.error("Task Name is required")
            return
        download_task = LLMRequestResultDownload.objects.filter(id=task_id).first()
        if download_task is None:
            raise Exception("Task not found")
        download_task.processed = "started"
        download_task.save()
        try:
            # limit the queryset to the number of rows per csv file
            if user_id is None:
                queryset = LLMRequestRecord.objects.filter(
                    name=task_name, success=True
                ).order_by("id")
            else:
                queryset = LLMRequestRecord.objects.filter(
                    name=task_name, success=True, user__id=user_id
                ).order_by("id")
            if not queryset.exists():
                logger.error(f"No records found for task_name: {task_name}")
                return

            paginator = Paginator(queryset, rows_per_csv)
            logger.info(f"Total number of pages: {paginator.num_pages}")

            csv_files = []
            for page_num in range(1, paginator.num_pages + 1):
                logger.info(f"Exporting {task_name} part {page_num}")
                page = paginator.page(page_num)
                resource = LLMRequestRecordResource()
                dataset = resource.export(page.object_list)

                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{settings.TMP_FOLDER}/{task_name}_{current_datetime}_part{page_num}.csv"

                with open(filename, "wb") as file:
                    file.write(dataset.csv.encode())

                logger.info(f"Exported {task_name} part {page_num} to csv file")
                logger.info(f"File path: {filename}")
                csv_files.append(filename)

            # then zip all the csv files
            zip_file_name = cls.zip_files(task_name=task_name, csv_files=csv_files)

            # upload to s3
            s3_client = settings.BOTO3_SESSION.client("s3")
            s3_client.upload_file(
                zip_file_name,
                settings.CSV_BUCKET,
                f"llm/{user_id or 'general'}/{task_name}/{zip_file_name.split('/')[-1]}",
            )

            download_task.download_link = (
                f"llm/{user_id or 'general'}/{task_name}/{zip_file_name.split('/')[-1]}"
            )
            download_task.progress = "completed"
            download_task.save()

            # then delete the csv files and the zip file
            for csv_file in csv_files:
                os.remove(csv_file)
            os.remove(zip_file_name)
        except Exception as e:
            download_task.progress = "failed"
            download_task.save()
            raise e

    @staticmethod
    def zip_files(task_name: str, csv_files: list):
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{settings.TMP_FOLDER}/{task_name}_{current_datetime}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zip_file:
            for csv_file in csv_files:
                zip_file.write(csv_file, arcname=csv_file.split("/")[-1])

        logger.info(f"Zipped all csv files to {zip_filename}")
        return zip_filename
