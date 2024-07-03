import torch

# Load model directly
from transformers import AutoModelForCausalLM, AutoTokenizer

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
        self.avail_tokenizers = {}

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
                hf_tokenizer = AutoTokenizer.from_pretrained(hf_model_name)
                hf_model = AutoModelForCausalLM.from_pretrained(hf_model_name)
                hf_model.to(device)
                self.avail_models[hf_model_name] = hf_model
                self.avail_tokenizers[hf_model_name] = hf_tokenizer

        with timer(logger, f"Model infer {hf_model_name}"):
            with time_tracker(
                "infer", latency_profile, track_type=TrackType.MODEL.value
            ):
                inputs = self.avail_tokenizers[hf_model_name](
                    text,
                    return_tensors="pt",
                    max_length=1024,
                    truncation=True,
                )
                # to device
                inputs = {k: v.to(hf_model.device) for k, v in inputs.items()}
                num_of_tokens = len(inputs["input_ids"][0])
                res = hf_model.generate(**inputs, max_new_tokens=num_of_tokens + 100)
                generated_text = self.avail_tokenizers[hf_model_name].decode(
                    res[0].cpu().tolist(), skip_special_tokens=True
                )
        result_profile["text"] = generated_text
        result_profile["logs"] = res[0].tolist()
        task.result_status = ResultStatus.completed.value
        task.result_json.result_profile.update(result_profile)
        task.result_json.latency_profile.update(latency_profile)
        TimeLogger.log_task(task, "end_hf_llm")
        return task
