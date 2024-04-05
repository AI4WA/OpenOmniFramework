from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)

SQL_SCRIPTS = [
    """
    DROP VIEW IF EXISTS view_live_worker;
    CREATE VIEW view_live_worker AS
    SELECT 
        task_type,
        COUNT(*) AS recent_update_count 
    FROM 
        worker_taskworker 
    WHERE 
        updated_at > NOW() - INTERVAL '1 minutes'
    GROUP BY 
        task_type;
    """,
    """
    DROP VIEW IF EXISTS view_llm_unique_task_name;
    CREATE VIEW view_llm_unique_task_name AS
    SELECT 
        user_id,
        name,
        COUNT(*) AS count
    FROM llm_llmrequestrecord
    GROUP BY 
        user_id, name;
    """,
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
