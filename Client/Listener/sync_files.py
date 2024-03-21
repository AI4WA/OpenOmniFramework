import argparse
import subprocess
import time

from constants import DATA_DIR
from utils import get_logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = get_logger(__name__)


class SyncHandler(FileSystemEventHandler):
    def __init__(self, src_path, dest_path, sshpass):
        super().__init__()
        self.src_path = src_path
        self.dest_path = dest_path
        self.sshpass = sshpass

    def on_any_event(self, event):
        if event.is_directory:
            return None
        else:
            if self.sshpass:
                subprocess.call(
                    ["sshpass", "-p", self.sshpass, 'rsync', '-avz', '--delete', self.src_path, self.dest_path])
            else:
                # wer can set up the authentication first, then we can use the rsync command
                subprocess.call(
                    ['rsync', '-avz', '--delete', self.src_path,
                     self.dest_path])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--src_directory", default=None,
                        help="The source directory to sync, this is normally the folder from the client end,"
                             "we can work it out",
                        type=str)

    parser.add_argument("--dest_ip", default=None,
                        help="The destination ip address to sync, this will be an ip, for hotspots, we can use the",
                        type=str)
    parser.add_argument("--dest_directory", default=None,
                        help="The destination directory to sync, this is normally the folder from the server end",
                        type=str)
    parser.add_argument("--dest_username", default=None,
                        help="The destination username to sync, this is normally the username from the server end",
                        type=str)
    parser.add_argument("--dest_password", default=None,
                        help="The destination password to sync, this is normally the password from the server end",
                        type=str)
    args = parser.parse_args()

    if args.src_directory is None:
        src_directory = f"{DATA_DIR.as_posix()}/"
    else:
        src_directory = args.src_directory

    if args.dest_ip is None:
        dest_ip = "172.20.10.4"
    else:
        dest_ip = args.dest_ip

    if args.dest_directory is None:
        dest_directory = '/Users/pascal/PhD/applications/Assistant/Client/Listener/data/'  # this is hard coded
    else:
        dest_directory = args.dest_directory

    if args.dest_username is None:
        dest_username = "pascal"  # this is hard coded
    else:
        dest_username = args.dest_username

    if args.dest_password is None:
        dest_password = None
    else:
        dest_password = args.dest_password

    dest_dir = f"{dest_username}@{dest_ip}:{dest_directory}"

    logger.info(f"src_directory: {src_directory}")
    logger.info(f"dest_dir: {dest_dir}")
    logger.info(f"dest_password: {dest_password}")
    event_handler = SyncHandler(src_directory, dest_path=dest_dir, sshpass=dest_password)
    observer = Observer()
    observer.schedule(event_handler, src_directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
