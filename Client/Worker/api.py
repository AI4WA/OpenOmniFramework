import json
import socket
from datetime import datetime
from typing import Optional

import getmac
import requests

from constants import API_DOMAIN
from utils import get_logger

logger = get_logger("GPU-Worker-API")


class API:
    def __init__(
        self,
        domain: str = API_DOMAIN,
        token: str = "",
        uuid: str = "",
        task_type: str = "gpu",
    ):
        self.domain = domain
        self.token = token
        self.task_type = task_type
        self.uuid = uuid
        self.mac_address = getmac.get_mac_address()
        self.ip_address = self.get_local_ip()

    def get_available_models(self):
        url = f"{self.domain}/llm/config"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        return r.json()

    def get_task(self):
        url = f"{self.domain}/queue_task/task/{self.task_type}/"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()

    def post_task_result(
        self,
        task_id: str,
        result_status: str,
        description: str,
        completed_in_seconds: Optional[float] = 0,
        result: Optional[dict] = None,
    ):
        url = f"{self.domain}/queue_task/{task_id}/update_result/"
        r = requests.post(
            url,
            data={
                "result_status": result_status,
                "description": description,
                "completed_in_seconds": completed_in_seconds,
                "success": result_status == "completed",
                "result": json.dumps(result) if result else None,
            },
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()

    def register_or_update_worker(self):
        """
        Register or update the GPU worker
        url = "queue_task/gpu_worker/"
        """
        try:
            url = f"{self.domain}/queue_task/worker/"
            r = requests.post(
                url,
                data={
                    "uuid": self.uuid,
                    "mac_address": self.mac_address,
                    "ip_address": self.ip_address,
                    "task_type": self.task_type,
                },
                headers={"Authorization": f"Token {self.token}"},
            )
            logger.info(f"POST {url} {r.status_code}")
            logger.info(r.json())
            return r.json()
        except Exception as e:
            logger.error(f"Error registering worker: {e}")

    @staticmethod
    def get_local_ip():
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't matter if the address is reachable
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception as e:
            logger.error(f"Error getting local IP: {e}")
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def get_chat(self):
        url = f"{self.domain}/chat/get_chat/"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()

    def post_chat(self, chat_uuid: str, message: str):
        url = f"{self.domain}/chat/respond/"
        r = requests.post(
            url,
            data={
                "chat_uuid": chat_uuid,
                "message": message,
            },
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()

    def get_chat_summary(self):
        url = f"{self.domain}/chat/summarize_chat/"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()

    def post_chat_summary(self, chat_uuid: str, summary: str):
        url = f"{self.domain}/chat/update_summarize_chat/"
        r = requests.post(
            url,
            data={
                "chat_uuid": chat_uuid,
                "message": summary,
            },
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.json())
        return r.json()
