from sentence_transformers import SentenceTransformer

from models.parameters import GeneralMLParameters
from models.task import ResultStatus, Task
from models.track_type import TrackType
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker
from utils.timer import timer

logger = get_logger("HFHandler")


class GeneralMLModel:
    def __init__(self):
        self.avail_models = {}

    def handle_task(self, task: Task) -> Task:
        """
        Handle the task
        Args:
            task (Task): The task to handle

        Returns:
            Updated task
        """
        TimeLogger.log_task(task, "start_general_ml")
        result_profile = {}
        latency_profile = {}
        general_ml_parameters = GeneralMLParameters(**task.parameters)
        text = general_ml_parameters.text
        general_model_name = general_ml_parameters.general_model_name
        params = general_ml_parameters.params
        if general_model_name not in self.avail_models:
            logger.error(f"Model {general_model_name} not loaded yet")
            with time_tracker(
                "init", latency_profile, track_type=TrackType.MODEL.value
            ):
                ml_model = self.load_model(general_model_name)
                self.avail_models[general_model_name] = ml_model

        else:
            ml_model = self.avail_models[general_model_name]

        with timer(logger, f"Model infer {general_model_name}"):
            with time_tracker(
                "infer", latency_profile, track_type=TrackType.MODEL.value
            ):
                res = self.infer(ml_model, general_model_name, text, params)
        result_profile["result"] = res

        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        TimeLogger.log_task(task, "end_general_ml")
        return task

    @staticmethod
    def load_model(general_model_name: str):
        """
        Load model
        Args:
            general_model_name (str): Model name

        Returns:

        """
        if general_model_name == "sentence_transformer":
            return SentenceTransformer("all-MiniLM-L6-v2")
        raise ValueError(f"Model {general_model_name} is not implemented")

    @staticmethod
    def infer(ml_model, general_model_name: str, text: str, params: dict):
        """
        Infer the model
        Args:
            ml_model: General model
            general_model_name (str): Model name
            text (str): Text
            params (dict): Model params

        Returns:

        """
        if general_model_name == "sentence_transformer":
            result = ml_model.encode(text)
            return result.tolist()
        logger.info(params)
        raise ValueError(f"Model {general_model_name} is not implemented")
