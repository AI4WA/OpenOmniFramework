import argparse
import uuid
from datetime import datetime

import cv2

from api import API
from constants import DATA_DIR
from utils import get_logger

logger = get_logger("video_acquire")

"""
PER_LENGTH = 1800  # 30 minutes

# the screen width and height
WIDTH = 640
HEIGHT = 480
FPS = 24.0

"""

# per length of the video
PER_LENGTH = 1800  # 30 minutes

# the screen width and height
WIDTH = 640
HEIGHT = 480
FPS = 24.0


class VideoAcquire:
    def __init__(
        self,
        width=WIDTH,
        height=HEIGHT,
        fps=FPS,
        per_video_length=PER_LENGTH,
        api_domain="",
        token="",
        home_id: int = None,
    ):
        """
        init the video acquire
        Args:
            width: (int) the width of the video
            height (int): the height of the video
            fps (float): the frame per second
            per_video_length (int): the length of the video
            api_domain (str): the domain of the api
            token (str): the token of the api
            home_id (int): the home id
        """
        self.uid = str(uuid.uuid4())
        self.data_dir = DATA_DIR / "videos" / self.uid  # the data dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.width = width  # the width and height of the video
        self.height = height  # the width and height of the video
        self.fps = fps  # frame per second
        self.per_video_length = per_video_length  # the length of the video
        self.api = API(domain=api_domain, token=token, home_id=home_id)
        self.api.register_device()

    def record(self):
        """
        start to record the video
        """
        segment_images = 60
        seconds = 0
        minutes = 1

        # init the recording
        cap = cv2.VideoCapture(0)
        # set the width and height
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        # set the frame per second
        cap.set(cv2.CAP_PROP_FPS, 24.0)
        # use the XVID codec
        fourcc = cv2.VideoWriter_fourcc(*"avc1")  # noqa

        cap_fps = cap.get(5)  # get the fps of the camera
        logger.info(f"the fps of the camera is {cap_fps}")

        start_time = datetime.now()
        filename = self.data_dir / (start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4")

        out = cv2.VideoWriter(
            filename.as_posix(), fourcc, self.fps, (self.width, self.height)
        )  # noqa
        logger.info("start to record the video")
        flag = True
        while flag:
            try:
                if (datetime.now() - start_time).seconds >= self.per_video_length:
                    # stop the recording and save the video when the time is up
                    logger.info(f"the recording is finished, saved to file: {filename}")
                    out.release()
                    # TODO: post the video to the server
                    self.api.post_video(self.uid, filename.as_posix().split("/")[-1])
                    # resume the recording
                    start_time = datetime.now()
                    filename = self.data_dir / (
                        start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".mp4"
                    )
                    out = cv2.VideoWriter(
                        filename.as_posix(), fourcc, FPS, (self.width, self.height)
                    )  # noqa
                else:
                    # read the frame
                    logger.debug("Try to process the frame")
                    ret, frame = cap.read()
                    if ret:
                        logger.debug("write the frame")
                        out.write(frame)
                        # cv2.imshow("frame", frame)
                        if seconds == segment_images:
                            logger.info("begin the next frame segment")
                            seconds = 0
                            minutes += 1
                        if seconds < segment_images:
                            image_dir = (
                                self.data_dir
                                / "frames"
                                / f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
                            )
                            image_dir.mkdir(parents=True, exist_ok=True)
                            cv2.imwrite(
                                (image_dir / f"{seconds}.jpg").as_posix(), frame
                            )
                            seconds += 1
                if cv2.waitKey(1) == ord("q"):
                    break
            except KeyboardInterrupt:
                break
        cap.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_domain", default="http://localhost:8000", help="API domain", type=str
    )
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument("--home_id", default=None, help="which home it is", type=str)

    args = parser.parse_args()
    logger.info("Initializing video acquisition...")
    # every 1 minute, record the video
    video_acquire = VideoAcquire(
        per_video_length=10,
        api_domain=args.api_domain,
        token=args.token,
        home_id=args.home_id,
    )
    video_acquire.record()
