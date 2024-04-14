from datetime import datetime
from typing import Optional

import requests

from constants import API_DOMAIN
from utils import get_logger, get_mac_address

logger = get_logger("API")


class API:
    def __init__(
        self,
        domain: str = API_DOMAIN,
        token: str = "",
        home_id: int = None,
    ):
        self.domain = domain
        self.token = token
        self.mac_address = get_mac_address()
        self.home_id = home_id

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
                "home": self.home_id,
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

    def get_spoken_speech(self):
        url = f"{self.domain}/hardware/speech/?home_id={self.home_id}"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})

        logger.info(f"get {url} {r.status_code}")
        logger.info(r.text)
        logger.info(r.json())
        if r.status_code != 200:
            return []
        return r.json()
