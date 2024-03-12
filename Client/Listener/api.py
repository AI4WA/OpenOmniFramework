from datetime import datetime
from utils import get_logger
from constants import API_DOMAIN
import requests

logger = get_logger("API")


class API:
    def __init__(self, domain: str = API_DOMAIN, token: str = ""):
        self.domain = domain
        self.token = token

    def post_audio(self, uid: str,
                   sequence_index: int,
                   text: str,
                   audio_file: str,
                   start_time: datetime,
                   end_time: datetime):
        url = f"{self.domain}/hardware/audio/"
        r = requests.post(url, data={"uid": uid,
                                     "sequence_index": sequence_index,
                                     "text": text,
                                     "audio_file": audio_file,
                                     "start_time": start_time,
                                     "end_time": end_time},
                          headers={"Authorization": f"Token {self.token}"})
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()

    def post_video(self,
                   uid: str,
                   video_file: str):
        url = f"{self.domain}/hardware/video/"
        data = {"uid": uid,
                "video_file": video_file}
        logger.info(data)
        r = requests.post(url, data=data,
                          headers={"Authorization": f"Token {self.token}"})
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()
