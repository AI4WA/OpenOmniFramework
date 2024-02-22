import glob
import os
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
        self.data_dir = DATA_DIR / "videos" / self.uid
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.width = width
        self.height = height
        self.fps = fps
        self.per_video_length = per_video_length

    def record(self):
        """
        start to record the video
        :return:
        """
        segment_images = 60
        i = 0
        j = 1

        # init the recording
        cap = cv2.VideoCapture(0)
        # set the width and height
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        # set the frame per second
        cap.set(cv2.CAP_PROP_FPS, 24.0)
        # use the XVID codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        # FPS = cap.get(5)  # 获取摄像头帧率   帧率为30
        # print("FPS: ", FPS)

        start_time = datetime.now()
        filename = self.data_dir / (start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.avi')
        out = cv2.VideoWriter(filename.as_posix(), fourcc, self.fps, (self.width, self.height))

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
                    out = cv2.VideoWriter(filename, fourcc, FPS, (self.width, self.height))
                else:
                    # 读取一帧视频
                    logger.info("Try to process the frame")
                    ret, frame = cap.read()
                    if ret:
                        logger.info("write the frame")
                        out.write(frame)
                        cv2.imshow('frame', frame)
                        if i == segment_images:
                            logger.info("begin the next record")
                            i = 0
                            j = j + 1
                        if i < segment_images:
                            image_dir = self.data_dir / "frames" / f"images{j}"
                            image_dir.mkdir(parents=True, exist_ok=True)
                            cv2.imwrite((image_dir / f"{i}.jpg").as_posix(), frame)
                            i = i + 1

                if cv2.waitKey(1) == ord('q'):
                    break
            except KeyboardInterrupt:
                break
        cap.release()


if __name__ == '__main__':
    logger.info('Initializing video acquisition...')
    video_acquire = VideoAcquire()
    video_acquire.record()
