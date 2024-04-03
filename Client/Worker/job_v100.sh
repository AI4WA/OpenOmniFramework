#!/bin/bash
#SBATCH --job-name=llm_v100
#SBATCH --output=result_v100.txt
#SBATCH --nodes=1
#SBATCH --time=03:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100:1
#SBATCH --mem=64G
module load cuda/11.6

cd $MYGROUP/Jarv5/Client/Worker/

source venv/bin/activate
python3 main.py --token f07d79cda0137abacd39258654090410650c2c0d