import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

import requests

from constants import API_DOMAIN
from utils import get_logger, get_mac_address

logger = get_logger("API")


class API:
    """
    This is used to communicate with the API.

    - Register the device
    - Post audio to the API
    - Post video to the API
    - [Optional] Queue speech to text
    """

    def __init__(
            self,
            domain: str = API_DOMAIN,
            token: str = "",
            home_id: Optional[int] = None,
            track_cluster: Optional[str] = None,
    ):
        """
        The API class for the responder

        It will require the token and the endpoint to communicate with the API.

        If you deploy the API to a cloud server, do not forget to change the domain to the server's domain.

        Args:
            domain (str): The domain of the API.
            token (str): The token for the API.
            home_id (int): The home ID.
            track_cluster (str): The track cluster.

        """
        self.domain = domain
        self.token = token
        self.mac_address = get_mac_address()
        self.home_id = home_id
        self.track_cluster = track_cluster

    def set_track_id(self):
        if self.track_cluster is None:
            return None
        uid = str(uuid4())
        uid = uid.replace("-", "")
        track_id = f"T-{self.track_cluster}-{uid}"
        logger.info(track_id)
        return track_id

    def register_device(
            self,
            device_name: Optional[str] = None,
            device_type: Optional[str] = None,
            description: Optional[str] = None,
    ):
        """
        Register the device to the API.
        Args:
            device_name (Optional[str]): The device name, you can name it if you want to distinguish it better later
            device_type (Optional[str]): The device type, this can be used to distinguish the device type
            description (Optional[str]): The description of the device

        Returns:

        """
        url = f"{self.domain}/hardware/register/"

        r = requests.post(
            url,
            data={
                "home": self.home_id,
                "mac_address": self.mac_address,
                "device_name": device_name,
                "device_type": device_type,
                "description": description,
            },
            headers={"Authorization": f"Token {self.token}"},
            timeout=30,
        )
        logger.info(url)

        logger.info(f"POST {url} {r.status_code}")

    def post_audio(
            self,
            uid: str,
            sequence_index: int,
            audio_file: str,
            start_time: datetime,
            end_time: datetime,
            track_id: str = None,
    ):
        """
        Post metadata of the audio to the API.
        Args:
            uid (str): uuid of the audio
            sequence_index (int): The sequence index of the audio in this loop, together with uuid,
                                  it can be used to identify the audio
            audio_file (str): Path to the audio file, which will be synced to the API disk storage via another parameter
            start_time (datetime): The start time of the audio
            end_time (datetime): The end time of the audio

        Returns:

        """
        url = f"{self.domain}/hardware/audio/"
        r = requests.post(
            url,
            data={
                "home": self.home_id,
                "uid": uid,
                "sequence_index": sequence_index,
                "audio_file": audio_file,
                "start_time": start_time,
                "end_time": end_time,
                "hardware_device_mac_address": self.mac_address,
                "track_id": track_id,
            },
            headers={"Authorization": f"Token {self.token}"},
            timeout=30,
        )
        logger.info(f"POST {url} {r.status_code}")
        if r.status_code != 201:
            return None
        return r.json()

    def post_video(
            self, uid: str, video_file: str, start_time: datetime, end_time: datetime
    ):
        """
        Post metadata of the video to the API.
        Args:
            uid (str): uuid of this video section
            video_file (str): Path to the video file, which will be synced to the API disk storage via another parameter
                              it will also hold the information in the file name about the start/end time
            start_time (datetime): The start time of the video
            end_time (datetime): The end time of the video
        Returns:

        """
        url = f"{self.domain}/hardware/video/"
        data = {
            "home": self.home_id,
            "uid": uid,
            "hardware_device_mac_address": self.mac_address,
            "video_file": video_file,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        logger.info(data)
        r = requests.post(
            url, data=data, headers={"Authorization": f"Token {self.token}"}, timeout=30
        )
        logger.info(f"POST {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()

    def queue_speech_to_text(
            self, uid: str, audio_index: str, start_time: datetime, end_time: datetime
    ) -> str:
        """
        Optional, used to queue the speech to text task
        Args:
            uid (str): uuid of the audio
            audio_index (str): The audio index, which can be used to identify the audio
            start_time (datetime): The start time of the audio
            end_time (datetime): The end time of the audio

        Returns:
            (str): The track id of the task

        """
        track_id = self.set_track_id()
        url = f"{self.domain}/queue_task/ai_task/"
        data = {
            "name": "speech_to_text",
            "task_name": "speech2text",
            "parameters": json.dumps(
                {
                    "uid": uid,
                    "home_id": self.home_id,
                    "audio_index": audio_index,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "hardware_device_mac_address": self.mac_address,
                }
            ),
            "track_id": track_id,
        }
        r = requests.post(
            url, data=data, headers={"Authorization": f"Token {self.token}"}, timeout=30
        )
        logger.info(f"POST {url} {r.status_code}")
        if r.status_code != 200:
            logger.info(data)
            return None
        logger.info(r.json())
        return track_id

    def get_storage_solution(self):
        """
        Get the storage solution from the API
        Returns:

        """
        url = f"{self.domain}/hardware/storage_solution/"
        r = requests.get(
            url, headers={"Authorization": f"Token {self.token}"}, timeout=30
        )
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        data = r.json()
        logger.info(data)
        return data.get("storage_solution", "volume")

    def upload_file(self,
                    source_file: str,
                    dest_path: str,
                    ):
        """
        Upload the file to the API
        """
        url = f"{self.domain}/hardware/upload_file/"
        files = {"file": open(source_file, "rb")}
        data = {
            "dest_path": dest_path,
        }
        r = requests.post(
            url,
            files=files,
            data=data,
            headers={"Authorization": f"Token {self.token}"},
            timeout=30,
        )
        logger.info(f"POST {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return True
