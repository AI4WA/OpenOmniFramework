import torch
import transformers

from models.parameters import HFParameters
from models.task import ResultStatus, Task
from models.track_type import TrackType
from utils.get_logger import get_logger
from utils.time_logger import TimeLogger
from utils.time_tracker import time_tracker
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
        TimeLogger.log_task(task, "start_hf_llm")
        result_profile = {}
        latency_profile = {}
        hf_parameters = HFParameters(**task.parameters)
        hf_model_name = hf_parameters.hf_model_name
        text = hf_parameters.text
        hf_model = self.avail_models.get(hf_model_name, None)
        if hf_model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.error(f"Model {hf_model_name} not loaded yet")
            with time_tracker(
                "init_model", latency_profile, track_type=TrackType.TRANSFER.value
            ):
                hf_model = transformers.pipeline(
                    task=hf_parameters.task,  # default is "text-generation"
                    model=hf_model_name,
                    torch_dtype=torch.float16,
                    device=device,
                )
                self.avail_models[hf_model_name] = hf_model

        messages = [
            {"role": "user", "content": text},
        ]
        with timer(logger, f"Model infer {hf_model_name}"):
            with time_tracker(
                "infer", latency_profile, track_type=TrackType.MODEL.value
            ):
                res = hf_model(messages)
        text = res[0]["generated_text"][-1]["content"]
        result_profile["text"] = text
        result_profile["logs"] = res
        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        TimeLogger.log_task(task, "end_hf_llm")
        return task
