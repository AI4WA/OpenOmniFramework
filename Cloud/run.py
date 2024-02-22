import threading
import camera
import keyboard
from logzero import logger
from getFeatures import getFeatures
import real_time
import time
import os
from TASKW import TASKW
import argparse
import torch

from openai import OpenAI
from text_to_sounds import streamed_audio

client = OpenAI(api_key='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')

def program1():   #摄像头线程\
    global thread_flag
    thread_flag = True
    logger.info('begin recording')
    camera.record()#open the camera for taking videos
    thread_flag = False

    # return



def program2():    #wisper线程
    # 录制音频，音转文+音频结束
    real_time.main()
    # return

def program3():     #数据分析
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden_size", default=64, type=int)
    parser.add_argument("--mid_size", default=768, type=int)
    parser.add_argument("--pretrained", default="bert-base-uncased", type=str)
    parser.add_argument("--head_sa", default=4, type=int)
    parser.add_argument("--head_ga", default=8, type=int)
    parser.add_argument("--dropout_m", default=0.5, type=float)
    parser.add_argument("--dropout_f", default=0.7, type=float)
    parser.add_argument("--outdim", default=512, type=int)
    parser.add_argument("--output_size", default=1, type=int)
    parser.add_argument("--dropout", default=0.5, type=float)
    parser.add_argument("--act", default='relu', type=str)
    parser.add_argument("--num_loop", default=1, type=int)
    parser.add_argument("--feature_dims", default=[768, 33, 709], type=list)  #t,a,v
    args = parser.parse_args()


    images_index = 1
    time.sleep(2)
    while thread_flag:
        path = f'frames/images{images_index}'
        path_text = f'texts/{images_index}.txt'
        if os.path.exists(path) and os.path.exists(path_text):

            gf = getFeatures('', 'D:/applications/anaconda/openface/FeatureExtraction.exe','pre-trained models/bert_cn')
            gf.handleImages(images_index)
            feature_V = gf.getVideoEmbedding('frames',images_index, pool_size=5)     # (n/5,709)
            feature_A = gf.getAudioEmbedding('audios', images_index)      #(94,33)
            text, feature_T = gf.getTextEmbedding('texts', images_index)        #(n+2,768)

            if feature_V.all()==0 and feature_T.all()==0:
                continue


            #test

            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            # data
            model = TASKW(args).to(device)

            # a =  model.load_state_dict(torch.load("pre-trained models/taskw-mosei_3part.pth"))
            # print(a['Model.'])

            model.load_state_dict({k.replace('Model.', ''): v for k, v in torch.load("pre-trained models/taskw-sims.pth").items()},strict=False)
            # model.load_state_dict(torch.load("pre-trained models/taskw-mosei_3part.pth"))
            output = model(feature_T, feature_A, feature_V)

            images_index = images_index + 1

            if output >=0:
                out_text = '积极情绪:'+text
            else:
                out_text = '消极情绪:'+text

            #openai api
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "你是一个富有情感的助手，你能根据提问者的不同情绪做出不同的回答,但如果情绪和问题是相同的，则答案也必须相同"},
                    {"role": "user",
                     "content": out_text}
                ],
                temperature = 0.0
            )
            print('input',out_text)
            print('system',completion.choices[0].message.content)
            streamed_audio(completion.choices[0].message.content, "tts-1", "alloy")
            print("next loop")

        else:
            time.sleep(2)
            print("i am run.py, i am waiting a text file")
            continue

        #-1: negative; +1: positive

    # return


if __name__=="__main__":

    #创建三个线程，分别运行两个程序
    thread1 = threading.Thread(target=program1)
    thread2 = threading.Thread(target=program2)
    thread3 = threading.Thread(target=program3)

    #启动3个线程
    thread1.start()
    thread2.start()
    thread3.start()

    #等待3个线程执行完毕
    thread1.join()
    thread2.join()
    thread3.join()



