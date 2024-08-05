from datetime import datetime

from models.task import Task
from utils.get_logger import get_logger

logger = get_logger(__name__)

"""
For the latency

If it is model, the name will start with model_xx, and it is a duration
If it is transfer time, the name will start with transfer_xx, and it is a duration
If it is just to log the timestamp, the name will start with ts_xx, and it is a timestamp
"""


class TimeLogger:

    @staticmethod
    def log_task(task: Task, name: str):
        """
        Log the time taken to execute a block of code
        Args:
            task (Task): The task to store the time
            name (str): The name of the block

        Returns:

        """
        # check whether the task has the latency profile

        TimeLogger.log(task.result_json.latency_profile, name)

    @staticmethod
    def log(profile: dict, name: str):
        """
        Log the time taken to execute a block of code
        Args:
            profile (dict): The profile to store the time
            name (str): The name of the block

        Returns:

        """
        logger.info(profile)
        logger.info(name)
        profile[f"ts_{name}"] = datetime.now()
