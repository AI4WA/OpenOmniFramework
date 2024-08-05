# Agent

The Agent component is the core of the system, which will be in charge of:

- Running the ML or AI models distributed in the system
    - Running the models which require intensive computation
    - LLM models
    - Text2Speech models
    - Emotion Recognition models
    - etc.

It is writen in Python, and it is a pretty standard Python project.

Each different task will have a subfolder within the `modules` folder

## Latency Logger

Key thing to notice is that we create two classes to log the time point and duration to profile the latency performance
of the models.

- `Agent/utils/time_logger.py`: log time point
- `Agent/utils/time_tracker.py`: track duration

## Docker setup

We also setup the docker for the Agent component, which is in the `Dockerfile` and `docker-compose.yml` file.

## Storage solution

How we handle the different storage solution is inside the `storage.py` file.

## Data

As we mentioned in the introduction, models will be need to be downloaded to the `data/models` folder, it is normally
automatically.

Unless you want to run our emotion detection model, if you want to do that, refer to our introduction page.