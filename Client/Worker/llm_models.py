import requests
from huggingface_hub import hf_hub_url
from llama_cpp import Llama
from tqdm import tqdm

from constants import LLM_MODEL_DIR
from utils import get_logger

logger = get_logger("GPU-Worker-LLM-MODEL-CONFIG")


class LLMModelConfig:
    def __init__(
        self,
        model_name: str,
        model_size: str,
        model_family: str,
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
        self.llm = None
        logger.debug(args)
        logger.debug(kwargs)

    def model_path(self):
        model_file = LLM_MODEL_DIR / self.model_family / self.filename
        if model_file.exists():
            return model_file
        if self.download_model():
            return model_file
        return None

    def download_model(self):
        """

        Returns:

        """

        download_url = hf_hub_url(repo_id=self.repo, filename=self.filename)
        logger.critical(f"Downloading model from {download_url}")
        model_general_folder = LLM_MODEL_DIR / self.model_family
        logger.critical(f"Model folder {model_general_folder}")
        model_general_folder.mkdir(parents=True, exist_ok=True)
        filename = model_general_folder / self.filename
        response = requests.get(download_url, stream=True)
        # Total size in bytes.
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024  # 1 Kilobyte
        logger.critical(f"Downloading {self.filename} to {model_general_folder}")
        logger.critical(f"Total size: {total_size}")
        progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
        with open(filename, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size != 0 and progress_bar.n != total_size:
            logger.error("ERROR, something went wrong")
            return False
        return True

    def init_llm(self):
        self.llm = Llama(
            model_path=self.model_path().as_posix(),
            n_gpu_layers=-1,
            embedding=True,
            n_ctx=4096
        )
