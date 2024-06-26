# the purpose of this function will be
# if file changed, upload it to the s3
import argparse
import time

import boto3
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from constants import DATA_DIR, S3_BUCKET
from utils import get_logger

logger = get_logger(__name__)

s3_client = boto3.client("s3")


class SyncHandler(FileSystemEventHandler):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--home_id",
        required=True,
        help="The home id to sync, this is normally the folder from the client end,"
        "we can work it out",
        type=int,
    )
    args = parser.parse_args()

    event_handler = SyncHandler(home_id=args.home_id)
    observer = Observer()
    observer.schedule(event_handler, DATA_DIR.as_posix(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
