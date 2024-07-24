"""
This is the storage module.

It will include two process

- One is to pull data down
- Another is upload data
"""
from utils.api import API
from utils.storage.local_sync_handler import LocalSyncHandler
from utils.storage.s3_sync_handler import S3SyncHandler
from utils.storage.api_sync_handler import APISyncHandler
import argparse
import subprocess
import time
from typing import Optional

import boto3
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils.api import API
from utils.constants import DATA_DIR
from utils.get_logger import get_logger

logger = get_logger(__name__)


class StorageSolution:
    def __init__(self,
                 api_domain: str,
                 token: str,
                 ):
        self.api_domain = api_domain
        self.token = token
        self.api = API(domain=api_domain, token=token)
        self.storage_solution = self.api.get_storage_solution()

    def sync_push_data(self):
        """
        Sync the data to the storage
        """
        if self.storage_solution == "volume":
            return
        if self.storage_solution == "s3":
            self.sync_push_s3()
        if self.storage_solution == "local":
            self.sync_push_local()
        if self.storage_solution == "api":
            self.sync_push_api()

    def sync_push_local(self):
        """
        Sync the data to the local network
        """
        observer = Observer()
        local_handler = LocalSyncHandler(
            src_path=str(DATA_DIR / "tts"),
            dest_path=self.dest_dir,
            sshpass=self.dest_password,
        )
        observer.schedule(local_handler, str(DATA_DIR / "tts"), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def sync_push_s3(self):
        """
        Sync the data to the s3
        """
        observer = Observer()
        s3_handler = S3SyncHandler(s3_client=boto3.client("s3"))
        observer.schedule(s3_handler, str(DATA_DIR / "tts"), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def sync_push_api(self):
        """
        Sync the data to the api
        """
        observer = Observer()
        api_handler = APISyncHandler(self.api)
        logger.info(str(DATA_DIR / "tts"))
        observer.schedule(api_handler, str(DATA_DIR / "tts"), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_domain", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
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
    storage_solution = StorageSolution(
        api_domain=args.api_domain,
        token=args.token,
    )
    storage_solution.sync_push_data()
