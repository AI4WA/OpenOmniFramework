from datetime import datetime
from sentence_transformers import SentenceTransformer
import torch
import transformers

from models.parameters import GeneralMLParameters
from models.task import Task
from utils.get_logger import get_logger
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
        result_profile = {}
        latency_profile = {}
        general_ml_parameters = GeneralMLParameters(**task.parameters)
        text = general_ml_parameters.text
        general_model_name = general_ml_parameters.general_model_name
        params = general_ml_parameters.params
        if general_model_name not in self.avail_models:
            logger.error(f"Model {general_model_name} not loaded yet")
            start_time = datetime.now()
            ml_model = self.load_model(general_model_name)
            self.avail_models[general_model_name] = ml_model
            latency_profile["model_init"] = (
                datetime.now() - start_time
            ).total_seconds()
        else:
            ml_model = self.avail_models[general_model_name]

        start_time = datetime.now()
        with timer(logger, f"Model infer {general_model_name}"):
            res = self.infer(ml_model, general_model_name, text, params)
        latency_profile["model_infer"] = (datetime.now() - start_time).total_seconds()
        result_profile["result"] = res

        task.result_status = "completed"
        task.result_json["result_profile"] = result_profile
        task.result_json["latency_profile"] = latency_profile

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
        raise ValueError(f"Model {general_model_name} is not implemented")
