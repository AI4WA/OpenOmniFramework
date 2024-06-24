# Development and Deployment

```bash
cd ./Client/Listener
# create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 audios_acquire.py --api_domain http://localhost:8000 --token xxx_create_a_token_from_api_xxx --model medium
# it then will start to listen to the audio and send it to the API
```

#### Video Acquisition

```bash
cd ./Client/Listener
# create a virtual environment, if you have done it for audio, you can skip this step
# python -m venv venv
source venv/bin/activate
# pip install -r requirements.txt
python3 videos_acquire.py --api_domain http://localhost:8000 --token xxx_create_a_token_from_api_xxx
```

#### File Sync

You will only need to run this when we deploy the client on the Raspberry Pi, and the Central Brain is running on a
server.

```bash
cd ./Client/Listener
# create a virtual environment, if you have done it for audio, you can skip this step
# python -m venv venv
source venv/bin/activate
# pip install -r requirements.txt
python3 sync_files.py # with proper configurations
# TODO: this needs further implementation to be more production-ready
```

#### Text to Speech

This is looping to check from the API side whether there is any new text to be spoken.

```bash
cd ./Client/Responder
# create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 text_to_speech.py --api_domain http://localhost:8000 --token xxx_create_a_token_from_api_xxx
```
