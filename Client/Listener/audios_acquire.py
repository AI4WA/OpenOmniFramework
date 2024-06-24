import argparse
import uuid
from datetime import datetime
from queue import Queue
from sys import platform
from time import sleep

import speech_recognition as sr

from api import API
from constants import DATA_DIR
from utils import get_logger, timer

logger = get_logger(__name__)


class AudioAcquire:
    def __init__(
        self,
        api_domain: str = "",
        token: str = "",
        home_id: str = "",
        energy_threshold: int = 5000,
        default_microphone: str = "pulse",
        record_timeout: int = 30000,
        sampling_time: float = 0.25,
    ):
        """
        The audio acquire class

        Args:
            api_domain (str): the api domain
            token (str): the api token
            home_id (str): the home id
            energy_threshold (int): the energy threshold for the audio
            default_microphone (str): the default microphone
            record_timeout (int): the record timeout
            sampling_time (float): the sampling time in seconds, default is 0.25
        """
        self.uid = str(uuid.uuid4())
        self.data_dir = DATA_DIR / "audio" / self.uid  # the data dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # api setup
        self.api = API(domain=api_domain, token=token, home_id=home_id)
        # register the device
        self.api.register_device()

        # the energy threshold for the microphone
        self.energy_threshold = energy_threshold
        # the default microphone
        self.default_microphone = default_microphone
        # the record timeout
        self.record_timeout = record_timeout
        # sampling time
        self.sampling_time = sampling_time

        # the audio index when record starts
        self.audio_index = 0
        logger.info(f"session uid: {self.uid}")
        logger.info(f"starting timestamp {datetime.now()}")
        self.source = self.get_source()

    def get_source(self):
        """
        Get the source of the audio
        Returns:

        """

        source = None

        if "linux" in platform:
            mic_name = self.default_microphone
            # to do the debug
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                logger.debug(index)
                logger.debug(name)
            if not mic_name or mic_name == "list":
                logger.info("Available microphone devices are: ")
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    logger.critical(f'Microphone with name "{name}" found')
                return
            else:
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    if mic_name in name:
                        logger.debug(index)
                        logger.debug(name)
                        source = sr.Microphone(sample_rate=16000, device_index=index)
                        break
        else:
            source = sr.Microphone(sample_rate=16000)
        return source

    def run(self):
        data_queue = Queue()
        sample_time_queue = Queue()
        recorder = sr.Recognizer()
        recorder.energy_threshold = self.energy_threshold
        recorder.dynamic_energy_threshold = False

        logger.critical(f"Using microphone {self.source}")

        with self.source:
            recorder.adjust_for_ambient_noise(self.source)

        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to receive audio data when recordings finish.
            Args:
                _:
                audio (sr.AudioData): An AudioData containing the recorded bytes.

            Returns:

            """
            with timer(logger, f"Recording {self.audio_index}"):
                data = audio.get_raw_data()
                wav_data = audio.get_wav_data()
                sample_time = datetime.now()
                data_queue.put(data)
                sample_time_queue.put(sample_time)

                curr_audio_dir = DATA_DIR / "audio" / self.uid
                curr_audio_dir.mkdir(parents=True, exist_ok=True)
                with open(
                    curr_audio_dir
                    / f"{self.audio_index}-{sample_time.strftime('%Y%m%d%H%M%S')}.wav",
                    "wb",
                ) as file:
                    file.write(wav_data)

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually, but SpeechRecognizer provides a nice helper.
        recorder.listen_in_background(
            self.source, record_callback, phrase_time_limit=self.record_timeout
        )  # phrase_time_limit continues to monitor the time

        last_sample_start_time = datetime.now()
        logger.info("Model loaded.")
        logger.info("Listening for audio...")

        while True:
            try:
                if not data_queue.empty():
                    logger.info("no more sound, start transform...")

                    data_queue.queue.clear()
                    last_sample_time = sample_time_queue.queue[-1]
                    sample_time_queue.queue.clear()

                    self.api.queue_speech_to_text(
                        self.uid,
                        audio_index=str(self.audio_index),
                        start_time=last_sample_start_time,
                        end_time=last_sample_time,
                    )
                    self.api.post_audio(
                        self.uid,
                        self.audio_index,
                        f"{self.audio_index}-{last_sample_time.strftime('%Y%m%d%H%M%S')}.wav",
                        last_sample_start_time,
                        last_sample_time,
                    )
                    last_sample_start_time = last_sample_time

                    sleep(self.sampling_time)
            except KeyboardInterrupt:
                break


def main():
    """
    The main function
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--api_domain", default="http://localhost:8000", help="API domain", type=str
    )
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument("--home_id", default=None, help="which home it is", type=str)

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
        "--default_microphone",
        default="pulse",
        help="Default microphone name for SpeechRecognition. "
        "Run this with 'list' to view available Microphones.",
        type=str,
    )

    args = parser.parse_args()

    audio_acquire = AudioAcquire(
        api_domain=args.api_domain,
        token=args.token,
        home_id=args.home_id,
        energy_threshold=args.energy_threshold,
        default_microphone=args.default_microphone,
        record_timeout=args.record_timeout,
    )
    audio_acquire.run()


if __name__ == "__main__":
    main()
