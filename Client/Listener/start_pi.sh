#!/bin/bash

source venv/bin/activate
export DISPLAY=:0.0

# Sync files process
nohup  python3 storage.py  --token c284262e850b8ac98e9174db620dc246ea6d9043 --api_domain http://192.168.50.113:8000 --dest_dir jarv5@192.168.50.113:/Users/jarv5/code/OpenOmniFramework/Client/Listener/ --dest_password jarv5 > sync_files.log 2>&1 &

# Videos acquisition process
nohup python3 videos_acquire.py --token c284262e850b8ac98e9174db620dc246ea6d9043 --api_domain http://192.168.50.113:8000 > videos_acquire.log 2>&1 &

# Audios acquisition process
nohup python3 audios_acquire.py --token c284262e850b8ac98e9174db620dc246ea6d9043 --track_cluster CLUSTER_GPT_4O_ETE_CONVERSATION --api_domain http://192.168.50.113:8000 --default_microphone "USB Device 0x46d:0x825" > audios_acquire.log 2>&1 &
