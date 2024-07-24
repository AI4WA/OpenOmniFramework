import subprocess

from watchdog.events import FileSystemEventHandler

from utils.get_logger import get_logger

logger = get_logger(__name__)


class LocalSyncHandler(FileSystemEventHandler):
    """
    Sync the files to disk when they are created, modified, moved or deleted
    """

    def __init__(self, src_path: str, dest_path: str, sshpass: str):
        """

        Args:
            src_path (str): The source path to sync
            dest_path (str): The destination path to sync
            sshpass (str): The password to ssh
        """
        super().__init__()
        self.src_path = src_path
        self.dest_path = dest_path
        self.sshpass = sshpass

    def on_any_event(self, event):
        """
        Sync the files to disk when they are created, modified, moved or deleted
        Args:
            event:

        Returns:

        """
        if event.is_directory:
            return None
        else:
            if self.sshpass:
                subprocess.call(
                    [
                        "sshpass",
                        "-p",
                        self.sshpass,
                        "rsync",
                        "-avz",
                        "--delete",
                        self.src_path,
                        self.dest_path,
                    ]
                )
            else:
                # wer can set up the authentication first, then we can use the rsync command
                subprocess.call(
                    ["rsync", "-avz", "--delete", self.src_path, self.dest_path]
                )
