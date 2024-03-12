import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class SyncHandler(FileSystemEventHandler):
    def __init__(self, src_path, dest_path):
        super().__init__()
        self.src_path = src_path
        self.dest_path = dest_path

    def on_any_event(self, event):
        if event.is_directory:
            return None
        else:
            subprocess.call(
                ["sshpass", "-p", "sunQIANG9337@", 'rsync', '-avz', '--delete', self.src_path, self.dest_path])


if __name__ == "__main__":
    src_directory = '/home/pascal/code/Assistant/Client/Listener'
    dest_directory = 'pascal@192.168.50.252:/User/pascal/Desktop/data/'
    event_handler = SyncHandler(src_directory, dest_directory)
    observer = Observer()
    observer.schedule(event_handler, src_directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
