from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import requests
import subprocess
from utils import get_logger, timer

logger = get_logger("Responder")
api_key = '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'  # Replace with your API key


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

    @staticmethod
    def text_to_speech_openai(content: str,
                              model: str = "tts-1",
                              voice: str = "alloy"):
        # API endpoint URL
        url = "https://api.openai.com/v1/audio/speech"

        # Headers with authorization
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Request payload
        data = {
            "model": model,
            "input": content,
            "voice": voice,
            "response_format": "mp3"
        }

        try:
            with timer(logger, "Request to OpenAI"):
                # Make a POST request to the OpenAI audio API
                response = requests.post(url, headers=headers, json=data, stream=True)

            # Check if the request was successful
            if response.status_code == 200:
                # Use ffmpeg to convert the MP3 audio to WAV format in memory
                process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'wav', '-'], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                wav_audio, ffmpeg_error = process.communicate(input=response.content)
                process.wait()

                if process.returncode == 0:
                    # Convert the WAV audio bytes to AudioSegment
                    audio_content = AudioSegment.from_wav(io.BytesIO(wav_audio))

                    # Play the audio
                    play(audio_content)
                else:
                    logger.info(f"FFmpeg error: {ffmpeg_error.decode()}")
            else:
                logger.error(f"Error: {response.status_code}\n{response.text}")
        except Exception as error:
            logger.error(f"Error in streamed_audio: {str(error)}")


if __name__ == "__main__":
    # Example text
    text = "Hello, this is a test of the text to speech conversion."
    # Convert text to speech and play
    # Text2Speech.text_to_speech_and_play(text)
    Text2Speech.text_to_speech_openai(text)
