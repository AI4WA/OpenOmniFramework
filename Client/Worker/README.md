# Worker

The purpose of this is to run the llama cpp with the GPU support, and still call the center server to get tasks.

## Architecture

The worker will loop and call API for GPU task.
Then it will based on the tasks to run the llama cpp with GPU support.