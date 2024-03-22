from datetime import datetime
from typing import Optional

import requests

from constants import API_DOMAIN
from utils import get_logger, get_mac_address

logger = get_logger("API")


class API:
    def __init__(self, domain: str = API_DOMAIN, token: str = ""):
        self.domain = domain
        self.token = token
        self.mac_address = get_mac_address()

    def register_device(
        self,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
        description: Optional[str] = None,
    ):
        url = f"{self.domain}/hardware/register/"

        r = requests.post(
            url,
            data={
                "mac_address": self.mac_address,
                "device_name": device_name,
                "device_type": device_type,
                "description": description,
            },
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(url)

        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())

    def post_audio(
        self,
        uid: str,
        sequence_index: int,
        text: str,
        audio_file: str,
        start_time: datetime,
        end_time: datetime,
    ):
        url = f"{self.domain}/hardware/audio/"
        r = requests.post(
            url,
            data={
                "uid": uid,
                "sequence_index": sequence_index,
                "text": text,
                "audio_file": audio_file,
                "start_time": start_time,
                "end_time": end_time,
                "hardware_device_mac_address": self.mac_address,
            },
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()

    def post_video(self, uid: str, video_file: str):
        url = f"{self.domain}/hardware/video/"
        data = {
            "uid": uid,
            "hardware_device_mac_address": self.mac_address,
            "video_file": video_file,
        }
        logger.info(data)
        r = requests.post(
            url, data=data, headers={"Authorization": f"Token {self.token}"}
        )
        logger.info(f"POST {url} {r.status_code}")
        #
        # r = requests.post(url,
        #                   data={
        #                         "uid": uid,
        #                         "video_file": video_file,
        #                         "hardware_device_mac_address": self.mac_address
        #                   },
        #                   headers={"Authorization": f"Token {self.token}",
        #                            'Content-Type': 'application/json'})
        #
        # logger.info(f"POST {url} {r.status_code}")
        # logger.info(r.text)

        logger.info(r.json())
        return r.json()

    def queue_speech_to_text(
        self, uid: str, audio_index: str, start_time: datetime, end_time: datetime
    ):
        url = f"{self.domain}/queue_task/stt/"
        data = {
            "uid": uid,
            "audio_index": audio_index,
            "start_time": start_time,
            "end_time": end_time,
            "hardware_device_mac_address": self.mac_address,
        }
        r = requests.post(
            url, data=data, headers={"Authorization": f"Token {self.token}"}
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()
