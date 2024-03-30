from datetime import datetime
import json
from typing import Optional

import requests

from constants import API_DOMAIN
from utils import get_logger

logger = get_logger("GPU-Worker-API")


class API:
    def __init__(self, domain: str = API_DOMAIN, token: str = ""):
        self.domain = domain
        self.token = token

    def get_available_models(self):
        url = f"{self.domain}/llm/config"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        return r.json()

    def get_task(self):
        url = f"{self.domain}/queue_task/gpu_task/"
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
