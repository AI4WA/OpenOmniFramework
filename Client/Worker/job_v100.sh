#!/bin/bash
#SBATCH --job-name=llm_v100
#SBATCH --output=result_v100.txt
#SBATCH --nodes=1
#SBATCH --time=03:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:2
#SBATCH --mem=128G
module load cuda/11.6

cd $MYGROUP/Jarv5/Client/Worker/

source venv/bin/activate
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
