import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from llm.llm_call.config import MODELS
from llm.models import LLMConfigRecords

from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Check or download models'

    def handle(self, *args, **options):
        """
        Loop through the MODELS dictionary and check if the model is in the database. If it is not, add it.
        :param args:
        :param options:
        :return:
        """

        for model_families in MODELS:
            model_family = model_families["name"]
            model_type = model_families["model_type"]
            for model_info in model_families["models"]:
                if not LLMConfigRecords.objects.filter(model_name=model_info["name"]).exists():
                    record = LLMConfigRecords(
                        model_name=model_info["name"],
                        model_size=model_info["size"],
                        model_family=model_family,
                        model_type=model_type,
                        repo=model_info["repo"],
                        filename=model_info["filename"],
                        available=False
                    )
                    record.save()
                    logger.critical(f"Added {model_info['name']} to the database")
                else:
                    logger.critical(f"{model_info['name']} is already in the database")

        for llm_model in LLMConfigRecords.objects.all():
            # get the filename, and check if it exists in the models directory
            model_folder = Path(settings.BASE_DIR / "llm" / "llm_call" / "models" / llm_model.model_family)
            model_path = model_folder / llm_model.filename
            if not model_path.exists():
                llm_model.download_model()

            if model_path.exists():
                llm_model.available = True
                llm_model.file_size = model_path.stat().st_size
                llm_model.save()
                logger.critical(f"{llm_model.model_name} is available")
