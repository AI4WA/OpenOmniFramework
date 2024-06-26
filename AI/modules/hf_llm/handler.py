from datetime import datetime

import torch
import transformers

from models.parameters import HFParameters
from models.task import Task
from utils.get_logger import get_logger
from utils.timer import timer

logger = get_logger("HFHandler")


class HFLLM:
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
        hf_parameters = HFParameters(**task.parameters)
        hf_model_name = hf_parameters.hf_model_name
        text = hf_parameters.text
        hf_model = self.avail_models.get(hf_model_name, None)
        if hf_model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.error(f"Model {hf_model_name} not loaded yet")
            start_time = datetime.now()
            hf_model = transformers.pipeline(
                task=hf_parameters.task,  # default is "text-generation"
                model=hf_model_name,
                torch_dtype=torch.float16,
                device=device,
            )
            self.avail_models[hf_model_name] = hf_model
            latency_profile["model_init"] = (
                datetime.now() - start_time
            ).total_seconds()
        start_time = datetime.now()
        messages = [
            {"role": "user", "content": text},
        ]
        with timer(logger, f"Model infer {hf_model_name}"):
            res = hf_model(messages)
        latency_profile["model_infer"] = (datetime.now() - start_time).total_seconds()
        text = res[0]["generated_text"][len(text) :]  # noqa
        result_profile["text"] = text
        result_profile["logs"] = res
        task.result_status = "completed"
        task.result_json["result_profile"] = result_profile
        task.result_json["latency_profile"] = latency_profile

        return task