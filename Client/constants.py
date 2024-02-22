import os
from utils import get_logger
from pathlib import Path

logger = get_logger(__name__)
# get parent of current folder as root
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = Path(ROOT_PATH) / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)
