import argparse
import io
import os
import time

from pydub import AudioSegment
from pydub.playback import play

from api import API
from constants import DATA_DIR
from utils import get_logger, get_mac_address, timer

logger = get_logger("Responder")


class Text2Speech:
    def __init__(self):
        pass

    @staticmethod
    def text_to_speech_and_play(content: str):
        # Convert text to speech
        with timer(logger, "Text to speech"):
            tts = gTTS(text=content, lang="en")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        with timer(logger, "Load audio"):
            # Load the audio into pydub
            audio = AudioSegment.from_file(mp3_fp, format="mp3")

        with timer(logger, "Play audio"):
            # Play the audio
            play(audio)

    @staticmethod
    def play_audio_file(text2speech_file: str):
        # Load the audio into pydub
        audio = AudioSegment.from_file(text2speech_file, format="mp3")

        # Play the audio
        play(audio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_domain", default="http://localhost:8000", help="API domain", type=str
    )
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument(
        "--home_id",
        help="Listen to which home",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    # Initialize the API
    api = API(
        domain=args.api_domain,
        token=args.token,
        home_id=args.home_id,
    )
    while True:
        # Convert text to speech and play
        speech_content = api.get_spoken_speech()

        if len(speech_content) == 0:
            time.sleep(0.25)
            logger.info("No speech content")
            continue

        item = speech_content[0]
        text = item["text"]
        text2speech_file = item["text2speech_file"]
        if text2speech_file:
            text2speech_file = DATA_DIR / text2speech_file
        if text2speech_file and text2speech_file.exists():
            Text2Speech.play_audio_file(text2speech_file)
        else:
            logger.info(f"No audio file for {text}")
            logger.info(f"Text to speech: {text}")
