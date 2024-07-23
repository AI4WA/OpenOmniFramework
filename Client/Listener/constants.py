import os
from pathlib import Path

from utils import get_logger

logger = get_logger(__name__)
# get parent of current folder as root
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = Path(ROOT_PATH) / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

API_DOMAIN = "http://localhost:8000"

STORAGE_SOLUTION_VOLUME = "volume"
STORAGE_SOLUTION_S3 = "s3"
STORAGE_SOLUTION_LOCAL = "local"


S3_BUCKET = "openomni"

"""
# get parent of current folder as root
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = Path(ROOT_PATH) / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

API_DOMAIN = "http://localhost:8000"

S3_BUCKET = "wa-data-and-llm-platform" => change this to your bucket name
"""
