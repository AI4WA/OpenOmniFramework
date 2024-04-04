from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)

SQL_SCRIPTS = [
    """
    CREATE VIEW view_live_gpu_worker AS
    SELECT COUNT(*) AS recent_update_count 
    FROM worker_gpuworker 
    WHERE updated_at > NOW() - INTERVAL '5 minutes';
    """
]


class Command(BaseCommand):
    help = "loop and run sql scripts"

    def handle(self, *args, **options):
        """
        Loop through the MODELS dictionary and check if the model is in the database. If it is not, add it.
        :param args:
        :param options:
        :return:
        """
        with connection.cursor() as cursor:
            for script in SQL_SCRIPTS:
                cursor.execute(script)
                logger.info(f"Executed script: {script}")
        logger.info("Finished running all scripts")
