# Jarv5: Aged Care Robot

We have three part components

- Data Collection
    - Video
    - Audio
    - Sync file to Central Brain
- Central Brain
    - API
    - STT (Perform better in host machine)
    - TTS (Perform better in host machine)
    - EMOJI
    - LLM (This should in client end)
- Data Output
    - Play Audio

## Data Collection

### Video

```bash
cd ./Client/Listener
source venv/bin/activate
# install packages if you have not
python3 videos_acquire.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --home_id 1
```

### Audio

```bash
cd ./Client/Listener
source venv/bin/activate
python3 audios_acquire.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --home_id 1
```

### File Sync From Edges to Centre Brain

```bash
cd ./Client/Listener
source venv/bin/activate
python3 sync_files.py
# python3 sync_files.py --dest_ip 146.118.70.154 --dest_directory /home/pascal/Assistant/Client/Listener/data --dest_username pascal
# python3 sync_to_s3.py --home_id 1 
```

## Central Brain

### API

```bash
cd ./API
docker compose -f docker-compose-jarv5-demo.yml up
```

### STT and TTS

Because we have not setup GPU support for our docker image, we need to run the STT model in the local environment.

```bash
cd ./API
source venv/bin/activate
export DEEPFACE_HOME=./ml/ml_models/model_data/deepface
export DB_SERVICE=localhost
python3 manage.py start_worker
```

### EMOJI

For same reason as STT, we need to run the EMOJI model in the local environment.

```bash
cd ./API
source venv/bin/activate
export DEEPFACE_HOME=./ml/ml_models/model_data/deepface
export DB_SERVICE=localhost
python3 manage.py emoji
```

### LLM

```bash
cd ./Client/Worker
source venv/bin/activate
python3 main.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8  --api_domain http://localhost:8000 --task_type gpu
```

## Data Output

### Play Audio

```bash
cd ./Client/Responder
source venv/bin/activate
python3 text_to_speech.py --token 3915a50a381a07d77d7b695bbdb0524c6e4004f8 --api_domain http://localhost:8000 --home_id 1
```
