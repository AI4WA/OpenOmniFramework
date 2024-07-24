import argparse
import io
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from api import API
from utils import get_logger, timer

logger = get_logger("Responder")


class PlaySpeech:
    @staticmethod
    def text_to_speech_and_play(content: str):
        """
        Convert text to speech and play
        Args:
            content (str): The content to be converted to speech

        Returns:

        """
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
    def play_audio_url(url: str):
        """
        Play audio file from the given
        Args:
            url (str): The URL of the audio file

        Returns:

        """
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        with NamedTemporaryFile(delete=True, suffix=".mp3") as temp_file:
            temp_file.write(response.content)
            temp_file.flush()  # Make sure all data is written to the file

            # Load the audio into pydub
            audio = AudioSegment.from_file(temp_file.name, format="mp3")

            # Play the audio
            play(audio)

    @staticmethod
    def play_audio_file(file_path: Path):
        """
        Play audio file from the given
        Args:
            file_path (Path): The path of the audio file

        Returns:

        """
        # Load the audio into pydub
        audio = AudioSegment.from_file(file_path, format="mp3")

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
            time.sleep(1)
            logger.info("No speech content")
            continue

        item = speech_content
        logger.info(item)
        tts_url = item["tts_url"]
        if tts_url:
            PlaySpeech.play_audio_url(tts_url)
        logger.info(f"No tts_url for {item}")
        text2speech_file = Path(item["text2speech_file"])
        if text2speech_file.exists():
            PlaySpeech.play_audio_file(text2speech_file)
        else:
            logger.error(f"No file for {item}")
        time.sleep(0.25)
