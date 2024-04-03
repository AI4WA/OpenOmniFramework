#!/bin/bash
#SBATCH --job-name=llm_p100
#SBATCH --output=result_p100.txt
#SBATCH --nodes=1
#SBATCH --time=03:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:p100:4
#SBATCH --mem=64G
module load cuda/12.4

cd $MYGROUP/Jarv5/Client/Worker/

source venv_p100/bin/activate
python3 main.py --token f07d79cda0137abacd39258654090410650c2c0d