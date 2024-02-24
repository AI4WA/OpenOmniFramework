from datetime import datetime
from utils import get_logger
from constants import API_DOMAIN
import requests

logger = get_logger("API")


class API:
    def __init__(self, domain: str = API_DOMAIN, api_key: str = ""):
        self.domain = domain
        self.api_key = api_key

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
                          headers={"Authorization": f"Bearer {self.api_key}"})
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()
