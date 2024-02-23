from datetime import datetime

import cv2
from utils import get_logger
import uuid
from constants import DATA_DIR

logger = get_logger("video_acquire")

# per length of the video
PER_LENGTH = 1800

# the screen width and height
WIDTH = 640
HEIGHT = 480
FPS = 24.0


class VideoAcquire:

    def __init__(self, width=WIDTH, height=HEIGHT, fps=FPS, per_video_length=PER_LENGTH):
        self.uid = str(uuid.uuid4())
        self.data_dir = DATA_DIR / "videos" / self.uid  # the data dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.width = width  # the width and height of the video
        self.height = height  # the width and height of the video
        self.fps = fps  # frame per second
        self.per_video_length = per_video_length  # the length of the video

    def record(self):
        """
        start to record the video
        :return:
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
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # noqa

        cap_fps = cap.get(5)  # 获取摄像头帧率   帧率为30
        logger.info("FPS: ", cap_fps)

        start_time = datetime.now()
        filename = self.data_dir / (start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.avi')
        out = cv2.VideoWriter(filename.as_posix(), fourcc, self.fps, (self.width, self.height))  # noqa

        flag = True
        while flag:
            try:
                if (datetime.now() - start_time).seconds >= self.per_video_length:
                    # 到达视频分段时长后停止录制
                    logger.info(f'the recording is finished, saved to file: {filename}')
                    out.release()
                    # 重新开始新的视频录制
                    start_time = datetime.now()
                    filename = self.data_dir / (start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.avi')
                    out = cv2.VideoWriter(filename.as_posix(), fourcc, FPS, (self.width, self.height))  # noqa
                else:
                    # 读取一帧视频
                    logger.info("Try to process the frame")
                    ret, frame = cap.read()
                    if ret:
                        logger.info("write the frame")
                        out.write(frame)
                        cv2.imshow('frame', frame)
                        if seconds == segment_images:
                            logger.info("begin the next record")
                            seconds = 0
                            minutes += 1
                        if seconds < segment_images:
                            image_dir = self.data_dir / "frames" / f"images_min_{minutes}"
                            image_dir.mkdir(parents=True, exist_ok=True)
                            cv2.imwrite((image_dir / f"{seconds}.jpg").as_posix(), frame)
                            seconds += 1
                if cv2.waitKey(1) == ord('q'):
                    break
            except KeyboardInterrupt:
                break
        cap.release()


if __name__ == '__main__':
    logger.info('Initializing video acquisition...')
    video_acquire = VideoAcquire(per_video_length=10)
    video_acquire.record()
