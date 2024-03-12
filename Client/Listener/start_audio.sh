#!/bin/bash

# remove the data audio folder as we will be the only one here
rm -rf ./data/audio/*

# based on the command line intake
source venv/bin/activate
python3 audios_acquire.py --api_domian $API_DOMAIN --token $TOKEN --model $MODEL
