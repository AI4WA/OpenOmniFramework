# Worker

The purpose of this is to run the llama cpp with the GPU support, and still call the center server to get tasks.

## Architecture

The worker will loop and call API for a GPU task.
Then it will be based on the tasks to run the llama cpp with GPU support.

## How to get it work

### Kaya

1. Pull the repo
2. Create the environment
   ```bash
   cd ./Client/Worker
    python3 -m venv venv
    source venv/bin/activate
    module load cuda/11.6 # then figure out the path of nvcc (for p100, it is 12.4)
    CUDACXX=/uwahpc/local/cuda-11.6/bin/nvcc
      CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=all-major" FORCE_CMAKE=1 
      pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --upgrade 
    # or sometimes, you only need 
    # CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --upgrade 
    # this will install the llama-cpp-python with the GPU support
    pip install -r requirements.txt
    ```
3. Run the worker
    ```bash
    python worker.py --token <token>
    ```
