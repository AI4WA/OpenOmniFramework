import logging
import time
from contextlib import contextmanager

from models.track_type import TrackType

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@contextmanager
def time_tracker(
    label: str, profile: dict, track_type: TrackType = TrackType.MODEL.value
):
    """
    Track the time taken to execute a block of code
    Args:
        label (str): The name of the block
        profile (dict): The profile to store the time
        track_type (str): The type of tracking
    """
    # It will be either model or transfer
    start_time = time.time()
    yield
    end_time = time.time()
    elapsed_time = end_time - start_time
    profile[f"{track_type}_{label}"] = elapsed_time
    logger.info(f"{label} took {elapsed_time} seconds")
