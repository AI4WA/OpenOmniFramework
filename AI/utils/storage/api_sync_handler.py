from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils.api import API

from utils.get_logger import get_logger
from utils.constants import DATA_DIR

logger = get_logger(__name__)


class APISyncHandler(FileSystemEventHandler):
    """
    Sync the files to s3 when they are created, modified, moved or deleted
    """

    def __init__(self, api: API):
        super().__init__()
        self.api = api

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type in ("created", "modified", "moved", "deleted"):
            # print(f"Event type: {event.event_type} - Path: {event.src_path}")
            # only process .avi and .wav files
            if event.src_path.split("/")[-1].split(".")[-1] not in ["mp4", "wav", "mp3"]:
                return None
            try:
                self.api.upload_file(
                    event.src_path,
                    f"Responder/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}",
                )
                logger.info(f"Uploaded file to server: {event.src_path}")
            except Exception as e:
                logger.error(f"Error uploading file to s3: {e}")
