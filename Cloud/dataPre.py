import os
import argparse
import pandas as pd
from glob import glob
from tqdm import tqdm
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import ffmpeg

class dataPre():
    def __init__(self, working_dir):
        self.working_dir = working_dir
        # self.ffmpeg = ffmpeg_dir
        self.img_index = 0

    def AlignFaces(self, input_dir, output_dir):
        """
        fetch faces from frames using MTCNN
        """
        print("Start Align Faces...")
        mtcnn = MTCNN(image_size=224, margin=0)
        face=[]

        frames_pathes = sorted(glob(os.path.join(self.working_dir, input_dir, f'images{self.img_index}', "*.jpg")))

        for frames_path in tqdm(frames_pathes):
            try:
                img = Image.open(frames_path)
                face.append(mtcnn(img))
            except Exception as e:
                print(e)
                continue
        return face


    # def FetchAudios(self, input_dir, output_dir):
    #     """
    #     fetch audios from videos using ffmpeg toolkits
    #     """
    #     print("Start Fetch Audios...")
    #     video_pathes = sorted(glob(os.path.join(self.working_dir, input_dir, '*.mp4')))
    #     for video_path in tqdm(video_pathes):
    #         output_path = video_path.replace(input_dir, output_dir).replace('.mp4', '.wav')
    #
    #         if not os.path.exists(os.path.dirname(output_path)):
    #             os.makedirs(os.path.dirname(output_path))
    #         # print(output_path)
    #         # print(video_path)
    #         # ffmpeg.input(video_path).output(output_path).run()
    #         print(output_path)
    #         print(video_path)
    #         cmd = f'{self.ffmpeg} -i ' + video_path + ' -f wav -vn ' + \
    #               output_path #+ ' -loglevel quiet'
    #         os.system(cmd)