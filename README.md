# Jarv5

**J**: Junction

**A**: Artificial

**R**: Responsibility

**V**: Versatile

**5**: To be Better than J.A.R.V.I.S

This is an end to end conversational AI system framework.

Video and Audio input are collected from hardware devices, then send to the API for the downstream processing.

The output in the end will be text and then transformed to speech.

Client side then will be notified to play the speech.

## Main Components

Three components:

- [Client](./docs/Client.md)
    - Input:
        - Audio
        - Video
    - Output:
        - Text to Speech
- [API](./docs/API.md):
    - Knowledge base (Relational Database + Graph Database)
    - Model Orchestration (LLM, GPT-4 API, self-developed models)
    - Data processing
- [Web](./docs/Web.md)
    - Chat interface
    - Data management

## Architecture

![Architecture](./docs/imgs/jarv5.png)

## Applications

### Aged Care

We'll start by developing a conversational AI system specifically designed for the aged care sector,
focusing on individuals who require nursing care at home.

Two main features:

- Monitoring and Nursing: Make sure they take their medication, eat well, and exercise regularly.
- Emotional Support: Provide companionship and emotional support.

## Development Environment Setup

To get this project end to end running, you need to set up the following:

- Client
    - Audio Acquisition
    - Video Acquisition
    - File Sync [Optional]
    - Text to Speech
- API
    - API
    - Audio Transcription
    - Emotion Recognition

Before you start, you will need to clone this repo to your local machine.

---

### Client

You will need to make sure your device includes the following hardware:

- Microphone
- Camera
- Speaker

Note: If you are running the client on Windows WSL, you probably cannot access the camera/microphone/speaker
directly [TODO].
You will need to run it on a real Windows machine via PowerShell.

#### Audio Acquisition

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

-----

### API

#### API Server

```bash
cd ./API
docker compose up
```

This should be able to start the API, and you can access

- admin: http://localhost:8000/
- api docs: http://localhost:8000/redoc

Username and password are `admin/password`.

#### Audio Transcription

It can be run within the container, actually, it is already running in the container, you can check the worker
container.
There is a `worker` container running in the background, listen for LLM queued tasks.

However, running inside containers will have much lower performance compared to running on the host machine.

So to get a more efficient transcription, you can run it on the host machine.

```bash
cd ./API
# create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt
export DB_SERVICE=localhost
python3 manage.py start_worker --task_type stt
```

#### Emotion Recognition

For the same reason as above (for now they both only running on CPU), we prefer to run it on the host machine.

```bash
cd ./API
# create a virtual environment if you haven't done it
# python3 -m venv venv
source venv/bin/activate
# pip install -r requirements.txt
# pip install -r requirements.dev.txt
export DB_SERVICE=localhost
python3 manage.py emoji
```

---

### Web

This is not a standalone application, but it can run against different API servers, which will be quite handy for
debugging.
It is an application written in React and Next.js.

You can then open the browser and go to http://localhost:3000

```bash
cd ./Web
docker compose up
```

