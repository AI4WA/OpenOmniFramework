import logging
from pathlib import Path

import requests
from django.conf import settings
from django.db import models
from huggingface_hub import hf_hub_url
from tqdm import tqdm

logger = logging.getLogger(__name__)


class LLMConfigRecords(models.Model):
    model_name = models.CharField(max_length=100)
    model_size = models.CharField(max_length=100)
    model_family = models.CharField(max_length=100)
    model_type = models.CharField(
        max_length=100,
        choices=[
            ("hf", "HuggingFace"),
            ("api", "API"),
            ("llama.cpp", "llama.cpp"),
            ("chatglm.cpp", "chatglm.cpp"),
        ],
        default="hf",
    )
    repo = models.CharField(max_length=100, blank=True, null=True)
    filename = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.FloatField(blank=True, null=True)
    available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def model_path(self):
        return Path(
            settings.BASE_DIR
            / "llm"
            / "llm_call"
            / "models"
            / self.model_family
            / self.filename
        )

    def download_model(self):
        """
        Download the model from the model_details
        :return:
        """
        download_url = hf_hub_url(repo_id=self.repo, filename=self.filename)
        logger.critical(f"Downloading model from {download_url}")

        model_general_folder = Path(
            settings.BASE_DIR / "llm" / "llm_call" / "models" / self.model_family
        )
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

    class Meta:
        verbose_name = "LLM Config Record"
        verbose_name_plural = "LLM Config Records"
