from utils import get_logger
from api import API
from typing import Optional
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import boto3
from constants import DATA_DIR, S3_BUCKET, STORAGE_SOLUTION_VOLUME, STORAGE_SOLUTION_S3, STORAGE_SOLUTION_LOCAL
import time
import argparse

logger = get_logger(__name__)


class S3SyncHandler(FileSystemEventHandler):
    """
    Sync the files to s3 when they are created, modified, moved or deleted
    """

    def __init__(self, home_id: int):
        super().__init__()
        self.home_id = home_id

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type in ("created", "modified", "moved", "deleted"):
            # print(f"Event type: {event.event_type} - Path: {event.src_path}")
            # only process .avi and .wav files
            if not event.src_path.endswith(".mp4") and not event.src_path.endswith(
                    ".wav"
            ):
                return None
            try:
                s3_client.upload_file(
                    event.src_path,
                    S3_BUCKET,
                    f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}",
                )
                logger.info(f"Uploaded file to s3: {event.src_path}")
                # logger.info(f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}")
            except Exception as e:
                logger.error(f"Error uploading file to s3: {e}")


class StorageHandler:
    def __init__(self,
                 api_domain: str = "",
                 token: str = "",
                 home_id: Optional[str] = "",
                 ):
        """
        Args:
            api_domain (str): the api domain
            token (str): the api token
            home_id (str): the home id
        """
        self.home_id = home_id
        self.api = API(domain=api_domain, token=token, home_id=home_id)
        self.storage_solution = self.api.get_storage_solution()

    def process(self):
        if self.storage_solution == STORAGE_SOLUTION_VOLUME:
            logger.info("No need to process files")
            return

        if self.storage_solution == STORAGE_SOLUTION_S3:
            self.process_s3()

    def process_s3(self):
        observer = Observer()
        observer.schedule(S3SyncHandler(self.home_id), str(DATA_DIR), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_domain", default="http://localhost:8000", help="API domain", type=str
    )
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument("--home_id", default=None, help="which home it is", type=str)
    args = parser.parse_args()

    storage_handler = StorageHandler(api_domain=args.api_domain, token=args.token, home_id=args.home_id)
    storage_handler.process()
