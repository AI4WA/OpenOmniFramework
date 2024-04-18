#!/bin/bash

source venv/bin/activate
export DISPLAY=:0.0

# Sync files process
nohup python3 sync_files.py --dest_ip 146.118.70.154 --dest_directory /home/pascal/Assistant/Client/Listener/data --dest_username pascal > sync_files.log 2>&1 &

# Sync to S3 process
nohup python3 sync_to_s3.py --home_id 1 > sync_to_s3.log 2>&1 &

# Videos acquisition process
nohup python3 videos_acquire.py --token 60a00917dbfb3fe21ebbeff8dc95de0f5ffba9a5 --home_id 1 --api_domain https://api.nlp-tlp.org > videos_acquire.log 2>&1 &

# Audios acquisition process
nohup python3 audios_acquire.py --token 60a00917dbfb3fe21ebbeff8dc95de0f5ffba9a5 --home_id 1 --api_domain https://api.nlp-tlp.org --default_microphone "USB Device 0x46d:0x825" > audios_acquire.log 2>&1 &
