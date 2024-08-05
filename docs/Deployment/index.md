# Deployment Guide

As we suggest in the introduction, we have four modes of deployment:

- [Trial on Cloud](./trial-on-cloud.md)
- [All in One Local Machine](./all-in-one-local-machine.md)
- [Private Offline Deployment](./private-offline-deployment.md)
- [Your Cloud](./your-cloud.md)

If you want to easily get start, you can use our deployed API, the link
is [https://openomni.ai4wa.com](https://openomni.ai4wa.com), to manage the tasks.

If you want to test out the full setup locally, you can follow the guide in the `All in One Local Machine` section.

If you are thinking about deploy it as a product, which is fully locally within a home network, addressing the privacy
issue, you can follow the guide in the `Private Offline Deployment` section.

If you are doing research with cluster of computing resources, or you want annotators to work on the same platform for a
serious project, you can follow the guide in the `Your Cloud` section.

---

## Modules

We have three components in the stack to deploy:

- API
- Agent
- Client
    - Listener (Audio and Video)
    - Responder (Audio)

### API

- Required Resource
    - A server (If on cloud will require a Public IP)
    - Minimum 1 CPU and 1 GB RAM
    - Deployment method:
        - For cloud server: Docker + Docker Compose + Nginx
        - For local server: Docker + Docker Compose

### Agent

- Required Resource
    - Any high-end computational Nvidia GPU resources
        - Can be HPC Clusters
        - Can work on demand, which means, you can spin the tasks when needed
        - Can work on CPU as well, but the performance will be degraded
    - Minimum storage of 500 GB
        - This is required to store the models and the data, especially the LLM models
    - Python 3.8+

### Client

- Required Resource:
    - Hardware:
        - Microphone: To gather the audio data
        - Camera: To gather the video data
        - Speaker: To play the audio data
        - Minimum 2 GB RAM
        - Minimum 1 CPU
        - Minimum 32 GB storage
        - It can be running on a laptop, or working with a Raspberry Pi
    - Python 3.8+

Something like this

![client](../images/client.jpg)

## Storage solution

All the metadata will be communicated via the API, so here we need to think about how can we share the video and audio
data between Agent/Client/API.

We have four **STORAGE_SOLUTION** for this four different scenarios:

- **api**: audio and video data will be upload and download via api endpoint, this is for the trial on cloud.
- **volume**: all the files will be shared on the same machine via the docker volume and file system, so there is no
  need to sync anything
- **local**: all the modules will be deployed on the same local network, but different machines, so we need to sync the
  data between them, with rsync
- **s3**: API is on your cloud, Agent is anywhere, so we will use *s3* to be the storage place for the data, to make sure
  stable
  and fast access.

To switch between these four modes, all you need to do is to set the `STORAGE_SOLUTION` environment variable before
start the API

```bash
export STORAGE_SOLUTION=api
```