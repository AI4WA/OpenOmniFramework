# OpenBenang

**Benang** means tomorrow in Western Australia Noongar Language.

![./docs/images/OpenBenang.png](./images/OpenBenang.png)

For an end to end conversational AI system, currently, there are mainly two approaches:

- Right side is what we think OpenAI GPT-4o is doing.
- Left side is what traditional conversational AI is doing.

As what OpenAI demonstrated in their video, they are doing the end to end model, which is quite impressive.
And in theory, it is the state of the art.

However, we do not know how they implement it, and why they can achieve that.
At the same time, fully end to end model is not easy to implement, one of the key reasons is that most of the
researchers do not have the resources(**Money** and **Data**) to train such a model.

To be able to reach what OpenAI is doing, we need crowd efforts, and we need everyone to focus on advancing their own
part, and do not need to waste time building the wheels.
Also, we need to allow this process be to high agile, which can allow people to easily test out their model,
understanding the real issues, and then improve it.
Another point is that, we need more data to advance the development of the system, for example, in a complex
conversational scenario,
we will want the system to be able to understand who is talking, what is the context, and what is the emotion.
This kind of data is lacking in the current dataset, and we need to find a way to generate this kind of data.

This is why we are building OpenBenang, which is a system that allows people to easily test out their model, it can be
an end to end model, or it can be a single component model within the pipeline.
It can also be easily deployed, so the researchers can collect the data they need with minimum effort to do the
adaptation.

Our ultimate goal is to:

- Develop an open-source, end-to-end conversational AI robot that surpasses the capabilities of OpenAI's GPT-4o.
- Enable easy data collection for advancing the development of end-to-end conversational AI systems.
- Inspire and foster the development of innovative conversational AI applications and products.

## System Operation Overview

1. **Data Collection:** Video and audio inputs are collected from hardware devices.
2. **Data Transfer:** Data is sent to the API for downstream processing.
3. **Data Processing:** The API uses AI and ML models to process the data, generate responses.
4. **Reaction:** The client side is notified to play the speech.

There are two key metrics we are focusing on:

- **Model Latency:** The time it takes for the model to generate a response.
- **Model Accuracy:** Whether the model generates the in-context response or accurate response.

In the end we will want to respond to the user's query in a timely manner, and provide the most in-context response.

## Main Components

From Application Development Perspective, we divide the whole applications into three main components:

- Client
- API
- AI
- Web

### Client

Detailed information can be found in [Client](./Client.md).

Client is decoupled from the API, to reduce the complexity of the system, and allow researchers or developers easily
integrate their own model into the system.

The client side will mainly in charge of

- Data Acquisition
    - Audio
    - Video
- Data Transfer
    - Transfer the data to storage places
- Data Presentation
    - Play the speech

### API

Detailed information can be found in [API](./API.md).

This is the **Brain** of the system, which will be in charge of:

- Knowledge Base
    - Relational Database
    - Graph Database
- Models Orchestration
    - LLM
    - GPT-4 API
    - Self-developed models
- API Interface
    - RESTful API
    - WebSocket API
- Data Management

### AI

Detailed information can be found in [AI](./AI.md).

- Running the ML or AI models
    - Running the models which require intensive computation
    - LLM models
    - Text2Speech models
    - Emotion Recognition models
    - etc.

The API side will work as the orchestrator, to manage the models, and provide the interface for the client to access

### Web

Detailed information can be found in [Web](./Web.md).

- It will provide a real-time interface for the user to view the progress of the end to end conversation process.
- It will also provide an interface for the user to doing the annotation, and evaluation of the system.

---

## Architecture

![Architecture](./images/ArchitectureDesign.jpg)


[//]: # ()

[//]: # (We have three part components)

[//]: # ()

[//]: # (- Data Collection)

[//]: # (    - Video)

[//]: # (    - Audio)

[//]: # (    - Sync files to Central Brain)

[//]: # (    - Sync files to S3)

[//]: # (- Central Brain)

[//]: # (    - API)

[//]: # (    - STT &#40;Better Perform locally in Central Brain / Performance Concern&#41;)

[//]: # (    - TTS &#40;Better Perform locally in Central Brain&#41;)

[//]: # (    - EMOJI &#40;Perform locally in Central Brain&#41;)

[//]: # (    - LLM &#40;This is in client end&#41;)

[//]: # (- Data Output)

[//]: # (    - Play Audio)

[//]: # ()

[//]: # (## Data Collection)

[//]: # ()

[//]: # (### Video)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./Client/Listener)

[//]: # (source venv/bin/activate)

[//]: # (# install packages if you have not)

[//]: # (python3 videos_acquire.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --home_id 1)

[//]: # (```)

[//]: # ()

[//]: # (### Audio)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./Client/Listener)

[//]: # (source venv/bin/activate)

[//]: # (python3 audios_acquire.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --home_id 1)

[//]: # (```)

[//]: # ()

[//]: # (### File Sync From Edges to Centre Brain)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./Client/Listener)

[//]: # (source venv/bin/activate)

[//]: # (python3 sync_files.py)

[//]: # (# python3 sync_files.py --dest_ip 146.118.70.154 --dest_directory /home/pascal/Assistant/Client/Listener/data --dest_username pascal)

[//]: # (# python3 sync_to_s3.py --home_id 1 )

[//]: # (```)

[//]: # ()

[//]: # (## Central Brain)

[//]: # ()

[//]: # (### API)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./API)

[//]: # (docker compose -f docker-compose-jarv5-demo.yml up)

[//]: # (```)

[//]: # ()

[//]: # (### STT and TTS)

[//]: # ()

[//]: # (Because we have not setup GPU support for our docker image, we need to run the STT model in the local environment.)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./API)

[//]: # (source venv/bin/activate)

[//]: # (export DEEPFACE_HOME=./ml/ml_models/model_data/deepface)

[//]: # (export DB_SERVICE=localhost)

[//]: # (python3 manage.py start_worker)

[//]: # (```)

[//]: # ()

[//]: # (### EMOJI)

[//]: # ()

[//]: # (For same reason as STT, we need to run the EMOJI model in the local environment.)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./API)

[//]: # (source venv/bin/activate)

[//]: # (export DEEPFACE_HOME=./ml/ml_models/model_data/deepface)

[//]: # (export DB_SERVICE=localhost)

[//]: # (python3 manage.py emoji)

[//]: # (```)

[//]: # ()

[//]: # (### LLM)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./Client/Worker)

[//]: # (source venv/bin/activate)

[//]: # (python3 main.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8  --api_domain http://localhost:8000 --task_type gpu)

[//]: # (```)

[//]: # ()

[//]: # (## Data Output)

[//]: # ()

[//]: # (### Play Audio)

[//]: # ()

[//]: # (```bash)

[//]: # (cd ./Client/Responder)

[//]: # (source venv/bin/activate)

[//]: # (python3 text_to_speech.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --api_domain http://localhost:8000 --home_id 1)

[//]: # (```)
