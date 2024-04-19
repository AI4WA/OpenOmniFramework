import argparse
import uuid
from datetime import datetime, timedelta
from queue import Queue
from sys import platform
from time import sleep

import numpy as np
import speech_recognition as sr
import torch
import whisper

from api import API
from constants import DATA_DIR
from utils import get_logger, timer

uid = str(uuid.uuid4())
logger = get_logger(f"audio_acquire_{uid}")


def main():
    """
    Output here should be
    - one sentence
    - the timestamp together with the sentence
    - the audio for this sentence

    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--energy_threshold",
        default=5000,
        help="Energy level for mic to detect.",
        type=int,
    )
    parser.add_argument(
        "--record_timeout",
        default=30000,
        help="How real time the recording is in seconds.",
        type=float,
    )

    parser.add_argument(
        "--api_domain", default="http://localhost:8000", help="API domain", type=str
    )
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument("--home_id", default=None, help="which home it is", type=str)

    if "linux" in platform:
        parser.add_argument(
            "--default_microphone",
            default="pulse",
            help="Default microphone name for SpeechRecognition. "
            "Run this with 'list' to view available Microphones.",
            type=str,
        )
    args = parser.parse_args()

    api = API(domain=args.api_domain, token=args.token, home_id=args.home_id)
    api.register_device()
    logger.info(f"session uid: {uid}")
    logger.info(f"starting timestamp {datetime.now()}")

    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    sample_time_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold
    # dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    # Represents whether the energy level threshold (see recognizer_instance.energy_threshold)
    # for sounds should be automatically adjusted based on the currently ambient noise level while listening.

    # Important for linux users.
    source = None
    # Prevents permanent application the app froze and crash by using the wrong Microphone
    if "linux" in platform:
        mic_name = args.default_microphone
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            logger.info(index)
            logger.info(name)
        if not mic_name or mic_name == "list":
            logger.info("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                logger.critical(f'Microphone with name "{name}" found')
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    logger.info(index)
                    logger.info(name)
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    if not source:
        logger.critical("No microphone found.")
        return

    logger.info(f"Using microphone {source}")

    record_timeout = args.record_timeout

    args.audio_index = 0

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        args.audio_index = args.audio_index + 1

        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        with timer(logger, f"Recording {args.audio_index}"):
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            wav_data = audio.get_wav_data()
            # this is the end time for the audio data
            sample_time = datetime.now()
            # the index 1 time is the start time, this will be the end time
            data_queue.put(data)
            sample_time_queue.put(sample_time)
            # get the file name with a timestamp, so it will not overwrite the previous one

            curr_audio_dir = DATA_DIR / "audio" / uid / "audio"
            curr_audio_dir.mkdir(parents=True, exist_ok=True)
            # 将录音数据写入.wav格式文件
            with open(
                curr_audio_dir
                / f"{args.audio_index}-{sample_time.strftime('%Y%m%d%H%M%S')}.wav",
                "wb",
            ) as file:
                file.write(wav_data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually, but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=record_timeout
    )  # phrase_time_limit持续监测时间

    last_sample_start_time = datetime.now()
    # Cue the user that we're ready to go
    logger.info("Model loaded.")
    logger.info("Listening for audio...")
    while True:
        try:
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():  # 当听不到声音后，开始transform
                logger.info("no more sound, start transform...")

                data_queue.queue.clear()
                last_sample_time = sample_time_queue.queue[-1]
                sample_time_queue.queue.clear()

                api.queue_speech_to_text(
                    uid,
                    audio_index=str(args.audio_index),
                    start_time=last_sample_start_time,
                    end_time=last_sample_time,
                )
                api.post_audio(
                    uid,
                    args.audio_index,
                    f"{args.audio_index}-{last_sample_time.strftime('%Y%m%d%H%M%S')}.wav",
                    last_sample_start_time,
                    last_sample_time,
                )
                last_sample_start_time = last_sample_time

                sleep(0.25)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
