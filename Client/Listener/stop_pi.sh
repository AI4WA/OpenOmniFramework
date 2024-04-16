#!/bin/bash
# Kill sync_files.py process
pkill -f 'python3 sync_files.py'

# Kill sync_to_s3.py process
pkill -f 'python3 sync_to_s3.py'

# Kill videos_acquire.py process
pkill -f 'python3 videos_acquire.py'

# Kill audios_acquire.py process
pkill -f 'python3 audios_acquire.py'
