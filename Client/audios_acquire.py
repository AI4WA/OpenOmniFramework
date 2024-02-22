import argparse
import numpy as np
import speech_recognition as sr
import whisper
import torch
from constants import DATA_DIR
from utils import get_logger, timer
from datetime import datetime, timedelta

from queue import Queue
from time import sleep
from sys import platform
import uuid

logger = get_logger("audio_acquire")


def main():
    """
    Output here should be
    - one sentence
    - the timestamp together with the sentence
    - the audio for this sentence

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_false',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--text_num", default=1,
                        help="How real time the recording is in seconds.", type=int)

    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    uid = str(uuid.uuid4())
    logger.info(f"session uid: {uid}")
    logger.info(f"starting timestamp {datetime.now()}")

    # The last time a recording was retrieved from the queue.
    phrase_time = None
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
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            logger.info("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                logger.critical(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    if not source:
        logger.critical("No microphone found.")
        return

    logger.info(f"Using microphone {source}")

    # Load / Download model
    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    logger.info(f"Loading model {model}...")
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = ['']

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

            curr_audio_dir = DATA_DIR / uid / "audio"
            # curr_audio_dir = DATA_DIR / "audio" / f"audio{args.text_num}"
            curr_audio_dir.mkdir(parents=True, exist_ok=True)
            # 将录音数据写入.wav格式文件
            with open(curr_audio_dir / f"{args.audio_index}-{sample_time.strftime('%Y%m%d%H%M%S')}.wav",
                      "wb") as file:
                file.write(wav_data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually, but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)  # phrase_time_limit持续监测时间

    # Cue the user that we're ready to go
    logger.info("Model loaded.")
    logger.info("Listening for audio...")

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():  # 当听不到声音后，开始transform
                logger.info('no more sound, start transform...')
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # the data in the queue should be a tuple of (data, time)
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                last_sample_time = sample_time_queue.queue[-1]
                sample_time_queue.queue.clear()

                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16-bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768 hz max.
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                logger.info(f"Model output: {result}")
                # get current time, this is the delay time for the audio to text data
                text = result['text'].strip()
                logger.info(f"delay time: {datetime.now() - last_sample_time}")

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise, edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text
                logger.critical(f"Transcription: {text}")
                # TODO: call API to push 1. text 2. text time range 3. related audio file

                # clear the console to reprint the updated transcription.
                # os.system('cls' if os.name == 'nt' else 'clear')
                text_dir = DATA_DIR / uid / "text"
                text_dir.mkdir(parents=True, exist_ok=True)

                with open(text_dir / f"{args.text_num}-{last_sample_time.strftime('%Y%m%d%H%M%S')}.txt", 'w',
                          encoding='utf-8') as f:
                    f.write(transcription[-1])  # 写入文本
                    args.text_num = args.text_num + 1
                # Infinite loops are bad for processors, must-sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

    logger.info("\n\nTranscription:")
    for line in transcription:
        logger.info(line)


if __name__ == "__main__":
    main()
