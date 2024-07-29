"""
This is the storage module.

It will include two process

- One is to pull data down
- Another is upload data
"""

import argparse
import multiprocessing
import time
from pathlib import Path

import boto3
import requests
from watchdog.observers import Observer

from utils.api import API
from utils.constants import CLIENT_DATA_FOLDER, DATA_DIR
from utils.get_logger import get_logger
from utils.storage.api_sync_handler import APISyncHandler
from utils.storage.local_sync_handler import LocalSyncHandler
from utils.storage.s3_sync_handler import S3SyncHandler

logger = get_logger(__name__)


class StorageSolution:
    def __init__(
        self,
        api_domain: str,
        token: str,
        dest_dir: str = None,
        dest_password: str = None,
    ):
        self.api_domain = api_domain
        self.token = token
        self.api = API(domain=api_domain, token=token)
        self.storage_solution = self.api.get_storage_solution()
        self.dest_dir = dest_dir
        self.dest_password = dest_password

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

    @staticmethod
    def sync_push_s3():
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

    def sync_pull_data(self):
        """
        If storage solution is volume or local, this means the data is accessible locally, do not need to worry about it
        This will first call cloud to list all audio and video files
        And then compare them with local ones
        If there is any new files, download them

        Returns:

        """
        if self.storage_solution == "volume":
            return
        if self.storage_solution == "local":
            self.sync_pull_api()
        if self.storage_solution == "s3":
            self.sync_pull_s3()
        if self.storage_solution == "api":
            self.sync_pull_api()

    def sync_pull_s3(self):
        """
        Sync the data from s3
        """
        pass

    def sync_pull_api(self):
        """
        Sync the data from api
        """
        from_time = None
        while True:
            try:
                logger.info(f"Syncing data from {from_time}")
                files = self.api.list_files(from_time=from_time)
                # set from time to now for the next sync in timestamp format
                from_time = time.time()
                self.download_data(files)
            except Exception as e:
                logger.error(f"Error syncing data: {e}")
            time.sleep(1)

    def download_data(self, files):
        """
        Download the data from the cloud
        Args:
            files:

        Returns:

        """
        audio_files = files.get("audio_files", [])
        video_files = files.get("video_files", [])
        logger.info(
            f"Checking {len(audio_files)} audio files and {len(video_files)} video files"
        )
        for audio_file in audio_files:
            dest_path = (
                CLIENT_DATA_FOLDER
                / "audio"
                / audio_file["uid"]
                / audio_file["audio_file"]
            )
            if not dest_path.exists():
                # TODO: do the download here
                logger.info(f"Downloading {audio_file['audio_file']} to {dest_path}")
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self.download_audio(audio_file["id"], dest_path)
        for video_file in video_files:
            dest_path = (
                CLIENT_DATA_FOLDER
                / "videos"
                / video_file["uid"]
                / video_file["video_file"]
            )
            if not dest_path.exists():
                # TODO: do the download here
                logger.info(f"Downloading {video_file['video_file']} to {dest_path}")
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self.download_video(video_file["id"], dest_path)

    def download_audio(self, audio_file_id, dest_path: Path):
        """
        Download the audio file
        Args:
            audio_file_id (str): the audio file id
            dest_path (str): the destination

        Returns:

        """
        link_json = self.api.download_file_link(audio_file_id, "audio")
        audio_url = link_json.get("audio_url", None)
        if audio_url is None:
            return

        try:
            r = requests.get(audio_url, stream=True)

            if r.status_code != 404:
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            else:
                logger.error(f"Error downloading audio file: {audio_url}, NOT FOUND")
        except Exception as e:
            logger.error(f"Error downloading audio file: {e}")

    def download_video(self, video_file_id, dest_path: Path):
        """
        Download the video file
        Args:
            video_file_id (str): the video file id
            dest_path (str): the destination

        Returns:

        """
        link_json = self.api.download_file_link(video_file_id, "video")
        video_url = link_json.get("video_url", None)
        frames = link_json.get("frames", None)
        logger.info(f"video_url: {video_url}, frames: {frames}")
        if video_url is not None:
            try:
                r = requests.get(video_url, stream=True)
                if r.status_code != 404:
                    with open(dest_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                else:
                    logger.error(
                        f"Error downloading video file: {video_url}, NOT FOUND"
                    )
            except Exception as e:
                logger.error(f"Error downloading video file: {e}")

        for frame_url in frames:
            # rsplit from the third /, get the last part

            frame_path = dest_path.parent / "frames" / frame_url.rsplit("/", 3)[-1]
            logger.info(f"Downloading frame {frame_url} to {frame_path}")
            if frame_path.exists():
                continue
            try:
                r = requests.get(frame_url, stream=True)
                with open(frame_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                logger.error(f"Error downloading frame file: {e}")


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
        dest_dir=args.dest_dir,
        dest_password=args.dest_password,
    )

    # Two process, on do the push, another do the pull
    p1 = multiprocessing.Process(target=storage_solution.sync_push_data)
    p2 = multiprocessing.Process(target=storage_solution.sync_pull_data)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
