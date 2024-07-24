import boto3
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils.api import API
from utils.constants import DATA_DIR, S3_BUCKET

from utils.get_logger import get_logger

logger = get_logger(__name__)


class S3SyncHandler(FileSystemEventHandler):
    """
    Sync the files to s3 when they are created, modified, moved or deleted
    """

    def __init__(self, s3_client):
        super().__init__()
        self.s3_client = s3_client

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type in ("created", "modified", "moved", "deleted"):
            # print(f"Event type: {event.event_type} - Path: {event.src_path}")
            # only process .avi and .wav files
            if event.src_path.split("/")[-1].split(".")[-1] not in ["mp4", "wav", "mp3"]:
                return None
            try:
                self.s3_client.upload_file(
                    event.src_path,
                    S3_BUCKET,
                    f"Responder/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}",
                )
                logger.info(f"Uploaded file to s3: {event.src_path}")
                # logger.info(f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}")
            except Exception as e:
                logger.error(f"Error uploading file to s3: {e}")
