from pathlib import Path

from llama_cpp import Llama


class LLMModelMemory:
    def __init__(
        self,
        model_name: str,
        model_size: str,
        model_family: str,
        model_path: Path,
        model_type: str,
        repo: str,
        filename: str,
        file_size: float,
        available: bool,
        *args,
        **kwargs,
    ):
        self.model_name = model_name
        self.model_size = model_size
        self.model_family = model_family
        self.model_type = model_type
        self.repo = repo
        self.filename = filename
        self.file_size = file_size
        self.available = available
        self.model_path = model_path
        self.llm = None

    def init_llm(self):
        self.llm = Llama(
            model_path=self.model_path.as_posix(), n_gpu_layers=-1, embedding=True
        )
