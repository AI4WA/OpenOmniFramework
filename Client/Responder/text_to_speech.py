import argparse
import io
import os
import time

from api import API
from constants import DATA_DIR
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from utils import get_logger, get_mac_address, timer

logger = get_logger("Responder")
api_key = os.environ.get("OPENAI_API_KEY")


class Text2Speech:
    def __init__(self):
        pass

    @staticmethod
    def text_to_speech_and_play(content: str):
        # Convert text to speech
        with timer(logger, "Text to speech"):
            tts = gTTS(text=content, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        with timer(logger, "Load audio"):
            # Load the audio into pydub
            audio = AudioSegment.from_file(mp3_fp, format="mp3")

        with timer(logger, "Play audio"):
            # Play the audio
            play(audio)

    #
    # @staticmethod
    # def text_to_speech_openai(content: str,
    #                           model: str = "tts-1",
    #                           voice: str = "alloy"):
    #     # API endpoint URL
    #     url = "https://api.openai.com/v1/audio/speech"
    #
    #     # Headers with authorization
    #     headers = {
    #         "Authorization": f"Bearer {api_key}"
    #     }
    #
    #     # Request payload
    #     data = {
    #         "model": model,
    #         "input": content,
    #         "voice": voice,
    #         "response_format": "mp3"
    #     }
    #
    #     try:
    #         with timer(logger, "Request to OpenAI"):
    #             # Make a POST request to the OpenAI audio API
    #             response = requests.post(url, headers=headers, json=data, stream=True)
    #
    #         # Check if the request was successful
    #         if response.status_code == 200:
    #             # Use ffmpeg to convert the MP3 audio to WAV format in memory
    #             process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'wav', '-'], stdin=subprocess.PIPE,
    #                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #             wav_audio, ffmpeg_error = process.communicate(input=response.content)
    #             process.wait()
    #
    #             if process.returncode == 0:
    #                 # Convert the WAV audio bytes to AudioSegment
    #                 audio_content = AudioSegment.from_wav(io.BytesIO(wav_audio))
    #
    #                 # Play the audio
    #                 play(audio_content)
    #             else:
    #                 logger.info(f"FFmpeg error: {ffmpeg_error.decode()}")
    #         else:
    #             logger.error(f"Error: {response.status_code}\n{response.text}")
    #     except Exception as error:
    #         logger.error(f"Error in streamed_audio: {str(error)}")

    @staticmethod
    def play_audio_file(audio_file: str):
        # Load the audio into pydub
        audio = AudioSegment.from_file(audio_file, format="mp3")

        # Play the audio
        play(audio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_domain", default="http://localhost:8000", help="API domain", type=str)
    parser.add_argument("--token", default="", help="API token", type=str)
    parser.add_argument("--listen_mac_address", help="Listen for which device output", type=str,
                        default=get_mac_address())
    args = parser.parse_args()

    # Initialize the API
    api = API(domain=args.api_domain, token=args.token, listen_mac_address=args.listen_mac_address)
    while True:
        # Convert text to speech and play
        speech_content = api.get_spoken_speech()

        if len(speech_content) == 0:
            time.sleep(0.25)
            logger.info("No speech content")
            continue
        # Text2Speech.text_to_speech_and_play(text)
        item = speech_content[0]
        text = item["text"]
        audio_file = item["audio_file"]
        if audio_file:
            audio_file = DATA_DIR / audio_file
        if audio_file and audio_file.exists():
            Text2Speech.play_audio_file(audio_file)

        else:
            logger.info(f"No audio file for {text}")
            logger.info(f"Text to speech: {text}")
            with timer(logger, "Text to speech"):
                Text2Speech.text_to_speech_and_play(text)
