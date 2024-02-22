import glob
import os
from datetime import datetime

import cv2
import logging
import pyaudio

logger = logging.getLogger(__name__)
import numpy as np

# 限制至少保留可用磁盘空间百分比
SPACE_LIMIT = 50
# 录制视频的分段时长(单位秒)
PER_LENGTH = 1800
# 视频保存位置
LOCATION = 'videos/'


# def disk_per():
#     """
#     计算当前/目录可用空间比率
#     :return: 返回整数百分比结果
#     """
#     info = os.statvfs('/')
#     free_size = info.f_bsize * info.f_bavail
#     total_size = info.f_blocks * info.f_bsize
#     percent = round(free_size / total_size * 100)
#     return percent


def get_files_list(exp):
    """
    获取指定位置下的指定后缀文件列表,根据文件创建时间正序排列(从早到后顺序)
    :param exp: 搜索路径表达式.格式: /home/pi/*.avi
    :return:
    """
    files = list(filter(os.path.isfile, glob.glob(exp)))
    # 按照文件创建时间倒序排列
    files.sort(key=lambda x: os.path.getctime(x), reverse=False)
    return files


def record():
    """
    录制视频
    :return:
    """
    segment_images = 60
    i = 0
    j = 1

    WIDTH = 640
    HEIGHT = 480
    FPS = 24.0
    # 初始话录制视频
    cap = cv2.VideoCapture(0)
    # 设置摄像头设备分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    # 设置摄像头设备帧率,如不指定,默认600
    cap.set(cv2.CAP_PROP_FPS, 24.0)
    # 建议使用XVID编码,图像质量和文件大小比较都兼顾的方案
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # FPS = cap.get(5)  # 获取摄像头帧率   帧率为30
    # print("FPS: ", FPS)

    start_time = datetime.now()
    filename = LOCATION + start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.avi'
    out = cv2.VideoWriter(filename, fourcc, FPS, (WIDTH, HEIGHT))

    flag = True
    while flag:
        try:
            # 检测磁盘空间是否充足
            # if disk_per() > SPACE_LIMIT:
            # 开始当前录制视频时段
            if (datetime.now() - start_time).seconds >= PER_LENGTH:
                # 到达视频分段时长后停止录制
                logger.info(f'分段录制结束，文件保存为{filename}')
                out.release()
                # 重新开始新的视频录制
                start_time = datetime.now()
                filename = LOCATION + start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.avi'
                out = cv2.VideoWriter(filename, fourcc, FPS, (WIDTH, HEIGHT))
            else:
                # 读取一帧视频
                ret, frame = cap.read()
                if ret:
                    # 保存视频
                    out.write(frame)
                    cv2.imshow('frame', frame)
                    if i == segment_images:
                        print("begin the next record")
                        i = 0
                        j = j + 1
                    if i < segment_images and os.path.exists(f"texts/{j}.txt"):  # check if the text have existed

                        path = f"frames/images{j}/"
                        if not os.path.exists(path):
                            os.mkdir(path)
                        cv2.imwrite(path + f"{i}.jpg", frame)
                        i = i + 1

            if cv2.waitKey(1) == ord('q'):
                break
        except KeyboardInterrupt:
            break

        # else:
        #     # 磁盘使用空间达到配额后删除最早的视频文件
        #     logger.warn(f'磁盘可用空间不足{SPACE_LIMIT}%,将删除最早保存的视频文件')
        #     files = get_files_list(LOCATION + '*.avi')
        #     os.remove(files[0])
        #     logger.info(f'{files[0]}已删除')

    cap.release()


if __name__ == '__main__':
    logger.info('开始录制视频')
    record()
