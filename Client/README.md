# Client

This is for the hardware side clients, which mainly includes two types:

- **Data Acquisition**
    - Audio
    - Video
- **Data Presentation**
    - Play the speech

The client side are quite light, it is tested and tried to be run on Raspberry Pi 4, and it is stable.

However, if you want to run a **Speech2Text** model on the client side, Raspberry Pi 4 is capable of running it, but it
will be slow.

## Listener

This module will be used to collect **Video** and **Audio** data from any devices with a camera and microphone.
It can be your laptop, it also can be your Raspberry Pi 4.

## Speaker

This module will be used to play the speech, which can be the output of the **Text2Speech** model.
You will need a speaker to play the sound.



---

## Development and Deployment

First, you will need to grab the token from the API side, and then come here to run the client side

And install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg
```

### Video

If you are using Raspberry Pi 4 or other devices with a camera but no GUI, you will need to set the display to the

```bash
export DISPLAY=:0.0

python3 
```