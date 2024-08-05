import socket

import getmac
import requests

from models.task import Task
from utils.get_logger import get_logger

from .constants import API_DOMAIN

logger = get_logger("AI-API")


class API:
    """
    This is the class to communicate with the API component
    """

    def __init__(
        self,
        domain: str = API_DOMAIN,
        token: str = "",
        uuid: str = "",
        task_name: str = "llm",
    ):
        """
        Init API class to communicate with the API
        Args:
            domain (str): The domain of the API
            token (str): The token to authenticate
            uuid (str): The UUID of the worker
            task_name (str): The task type of the worker
        """
        self.domain = domain
        self.token = token
        self.task_name = task_name
        self.uuid = uuid
        self.mac_address = getmac.get_mac_address()
        self.ip_address = self.get_local_ip()

    def verify_token(self) -> bool:
        try:
            url = f"{self.domain}/authenticate/api/token/verify/"
            r = requests.post(
                url,
                headers={"Authorization": f"Token {self.token}"},
                data={"token": self.token},
            )
            logger.info(f"POST {url} {r.status_code}")
            logger.info(r.json())
            if r.status_code != 200:
                return False
            return True
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False

    def get_available_models(self):
        """
        Get the available LLM models from the API
        Returns:

        """
        url = f"{self.domain}/llm/config"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        return r.json()

    def get_task(self):
        """
        Get the task from the API
        Returns:

        """
        logger.debug(self.task_name)
        url = f"{self.domain}/queue_task/task/{self.task_name}/"
        r = requests.get(url, headers={"Authorization": f"Token {self.token}"})
        logger.info(f"GET {url} {r.status_code}")
        logger.info(r.text)
        if r.status_code != 200:
            return None
        return r.json()

    def post_task_result(
        self,
        task: Task,
    ):
        """
        Post the task result to the API
        Args:
            task[Task]: The task to post the result

        Returns:

        """
        url = f"{self.domain}/queue_task/{task.id}/update_result/"
        r = requests.post(
            url,
            data=task.json(),
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/json",
            },
        )
        logger.info(f"POST {url} {r.status_code}")
        logger.info(r.text)
        if r.status_code != 200:
            return None
        return r.json()

    def register_or_update_worker(self):
        """
        Register or update the  worker
        So we can know whether the worker is alive or not
        """
        try:
            url = f"{self.domain}/queue_task/worker/"
            r = requests.post(
                url,
                data={
                    "uuid": self.uuid,
                    "mac_address": self.mac_address,
                    "ip_address": self.ip_address,
                    "task_name": self.task_name,
                },
                headers={"Authorization": f"Token {self.token}"},
            )
            logger.info(f"POST {url} {r.status_code}")
            # logger.info(r.text)
            return r.json()
        except Exception as e:
            logger.error(f"Error registering worker: {e}")

    @staticmethod
    def get_local_ip() -> str:
        """
        Get the local IP address
        Returns:
            str: The local IP address

        """
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

    def upload_file(
        self,
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

    def list_files(self, from_time=None):
        """
        List the files from the API
        """
        url = f"{self.domain}/hardware/list_files/"
        data = {
            "from_time": from_time,
        }
        r = requests.get(
            url,
            data=data,
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()

    def download_file_link(self, file_id, file_type):
        """
        Get the download file link
        """
        url = f"{self.domain}/hardware/download_file_link/"
        data = {
            "file_id": file_id,
            "file_type": file_type,
        }

        r = requests.get(
            url,
            data=data,
            headers={"Authorization": f"Token {self.token}"},
        )
        logger.info(f"GET {url} {r.status_code}")
        if r.status_code != 200:
            return None
        return r.json()