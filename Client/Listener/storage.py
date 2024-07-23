import argparse
import subprocess
import time
from typing import Optional

import boto3
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from api import API
from constants import (
    DATA_DIR,
    S3_BUCKET,
    STORAGE_SOLUTION_LOCAL,
    STORAGE_SOLUTION_S3,
    STORAGE_SOLUTION_VOLUME,
    STORAGE_SOLUTION_API
)
from utils import get_logger

logger = get_logger(__name__)


class LocalSyncHandler(FileSystemEventHandler):
    """
    Sync the files to disk when they are created, modified, moved or deleted
    """

    def __init__(self, src_path: str, dest_path: str, sshpass: str):
        """

        Args:
            src_path (str): The source path to sync
            dest_path (str): The destination path to sync
            sshpass (str): The password to ssh
        """
        super().__init__()
        self.src_path = src_path
        self.dest_path = dest_path
        self.sshpass = sshpass

    def on_any_event(self, event):
        """
        Sync the files to disk when they are created, modified, moved or deleted
        Args:
            event:

        Returns:

        """
        if event.is_directory:
            return None
        else:
            if self.sshpass:
                subprocess.call(
                    [
                        "sshpass",
                        "-p",
                        self.sshpass,
                        "rsync",
                        "-avz",
                        "--delete",
                        self.src_path,
                        self.dest_path,
                    ]
                )
            else:
                # wer can set up the authentication first, then we can use the rsync command
                subprocess.call(
                    ["rsync", "-avz", "--delete", self.src_path, self.dest_path]
                )


class S3SyncHandler(FileSystemEventHandler):
    """
    Sync the files to s3 when they are created, modified, moved or deleted
    """

    def __init__(self, home_id: int, s3_client):
        super().__init__()
        self.home_id = home_id
        self.s3_client = s3_client

    def on_any_event(self, event):
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
                self.s3_client.upload_file(
                    event.src_path,
                    S3_BUCKET,
                    f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}",
                )
                logger.info(f"Uploaded file to s3: {event.src_path}")
                # logger.info(f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}")
            except Exception as e:
                logger.error(f"Error uploading file to s3: {e}")


class APISyncHandler(FileSystemEventHandler):
    """
    Sync the files to s3 when they are created, modified, moved or deleted
    """

    def __init__(self, home_id: int, api: API):
        super().__init__()
        self.home_id = home_id
        self.api = api

    def on_any_event(self, event):
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
                self.api.upload_file(
                    event.src_path,
                    f"Listener/{event.src_path.split(DATA_DIR.as_posix())[1].strip('/')}",
                )
                logger.info(f"Uploaded file to server: {event.src_path}")
            except Exception as e:
                logger.error(f"Error uploading file to s3: {e}")


class StorageHandler:
    def __init__(
            self,
            api_domain: str = "",
            token: str = "",
            home_id: int = None,
            dest_dir: Optional[str] = None,
            dest_password: Optional[str] = None,
    ):
        """
        Args:
            api_domain (str): the api domain
            token (str): the api token
            home_id (int): the home id
            dest_dir (str): the destination directory to sync, like
            dest_password (str): the destination password to sync
        """
        self.home_id = home_id
        self.dest_dir = dest_dir
        self.dest_password = dest_password
        self.api = API(domain=api_domain, token=token, home_id=home_id)
        self.storage_solution = self.api.get_storage_solution()

    def process(self):
        if self.storage_solution == STORAGE_SOLUTION_VOLUME:
            logger.info("No need to process files")
            return

        if self.storage_solution == STORAGE_SOLUTION_S3:
            self.process_s3()

        if self.storage_solution == STORAGE_SOLUTION_LOCAL:
            self.process_local_network()

        if self.storage_solution == STORAGE_SOLUTION_API:
            self.process_api()

    def process_s3(self):
        observer = Observer()
        s3_handler = S3SyncHandler(self.home_id, s3_client=boto3.client("s3"))
        observer.schedule(s3_handler, str(DATA_DIR), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def process_local_network(self):
        observer = Observer()
        local_handler = LocalSyncHandler(
            src_path=str(DATA_DIR),
            dest_path=self.dest_dir,
            sshpass=self.dest_password,
        )
        observer.schedule(local_handler, str(DATA_DIR), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def process_api(self):
        observer = Observer()
        api_handler = APISyncHandler(self.home_id, self.api)
        observer.schedule(api_handler, str(DATA_DIR), recursive=True)
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
    parser.add_argument(
        "--dest_dir",
        default=None,
        help="The destination directory to sync, like root@xx.x.xx.x:/path/to",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--dest_password",
        default=None,
        help="The destination password to sync",
        type=str,
    )
    args = parser.parse_args()

    storage_handler = StorageHandler(
        api_domain=args.api_domain,
        token=args.token,
        home_id=args.home_id,
        dest_dir=args.dest_dir,
        dest_password=args.dest_password,
    )
    storage_handler.process()
