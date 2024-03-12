#!/bin/bash

export DISPLAY=:0.0

# remove the data video folder as we will be the only one here
rm -rf ./data/video/*

# based on the command line intake
source venv/bin/activate
python3 videos_acquire.py --api_domain $API_DOMAIN --token $TOKEN
