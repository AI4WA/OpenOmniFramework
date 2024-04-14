#!/bin/bash
source venv/bin/activate
# Infinite loop to keep running the command
while true; do
    # Run the command
    python3 main.py --token 221d6c1982662ee3e5e6178f67040c72ce6685fb --task_type gpu

    # Check the exit status of the command
    if [ $? -ne 0 ]; then
        echo "Command failed, restarting in 5 seconds..."
        sleep 5
    else
        echo "Command executed successfully, exiting loop."
        break
    fi
done
