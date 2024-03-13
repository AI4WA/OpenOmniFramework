#!/bin/bash

# start within hotspot network

export DISPLAY=:0.0
export API_DOMAIN=http://172.20.10.4:8000
export DEST_IP=172.20.10.4
# get the token from the input of the command line
TOKEN=$1
export TOKEN=$TOKEN
export MODEL=base

echo TOKEN: $TOKEN