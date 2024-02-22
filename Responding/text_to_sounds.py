import requests
from pydub import AudioSegment
from pydub.playback import play
import subprocess
import io

# Set your OpenAI API key
api_key = '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' # Replace with your API key

# Function to convert text to speech and play it
def streamed_audio(input_text, model, voice):
    # API endpoint URL
    url = "https://api.openai.com/v1/audio/speech"

    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Request payload
    data = {
        "model": model,
        "input": input_text,
        "voice": voice,
        "response_format": "mp3"
    }

    try:
        # Make a POST request to the OpenAI audio API
        response = requests.post(url, headers=headers, json=data, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Use ffmpeg to convert the MP3 audio to WAV format in memory
            process = subprocess.Popen(['ffmpeg', '-i', '-', '-f', 'wav', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            wav_audio, ffmpeg_error = process.communicate(input=response.content)
            process.wait()

            if process.returncode == 0:
                # Convert the WAV audio bytes to AudioSegment
                audio_content = AudioSegment.from_wav(io.BytesIO(wav_audio))
                
                # Play the audio
                play(audio_content)
            else:
                print(f"FFmpeg error: {ffmpeg_error.decode()}")
        else:
            print(f"Error: {response.status_code}\n{response.text}")
    except Exception as error:
        print(f"Error in streamed_audio: {str(error)}")

# # Usage example:
# input_model = "tts-1"  # Specify your desired model
# input_text = "Hello world! This is Grace. Good afternoon. How can I help you?"
# input_voice = "alloy"  # Specify the voice you want to use
# streamed_audio(input_text, input_model, input_voice)
