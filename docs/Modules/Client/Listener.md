# Listener

This is to collect the audio and video data from any devices with a camera and microphone. It can be your laptop, it
also can be your Raspberry Pi 4.

Collect the video is easy, just keep in the background, and record the video when needed, upload it to the API.

However, collect the audio is a bit tricky, which can be further enhanced.

## Audio

Our solution for the audio is using the whisper model to detect when user stop talking, your can specific the energy
threshold or timeout milliseconds to determine when to stop and save this round of sound.

This will get the API receive the audio in a "conversation" way, speaker stop, AI process and act, then speaker speak
again.

However, there are several situations are limited by current solution:

- multiple speakers: if we add another module to detect the speaker, then the latency will increase again
- interrupt: if the speaker interrupt the AI, then the AI should stop and listen to the speaker again, or interrupt the
  speaker, which GPT-4o is capable of doing
- streaming: on the other end, this means the audio data should be streamed to the API, which is not supported by the
  current solution

But it does can handle the basic conversation for research purpose.

There are several parameters you can specify when you start the audio listener:

- `--api_domain`: the API domain, default is `http://localhost:8000`, which is within the full local setup
- `--token`: the token you get from the API side
- `--home_id`: If you use cloud mode, you can have multiple homes to upload video and audio data, as one of the most
  common user case for this could be home intelligent assistant. The home do not limit to an actual home, can be a
  hospital room, etc.
- `--energy_threshold`: the energy threshold to determine when to stop the audio recording, default is `5000`
- `--timeout`: the timeout milliseconds to determine when to stop the audio recording, default is `30000` in
  milliseconds
- `default_microphone`: which microphone to use if there are multiple microphones, default is `pulse`
- `track_cluster`: the cluster you want to track, default is `CLUSTER_GPT_4O_ETE_CONVERSATION`

## Video

Video also in theory should be streaming to a model, however, currently most models do not have the capability to take
streaming input.

At the same time, most model is taking the images to the model.

So how we design it now is:

- every 20 seconds or duration you specify, we will record a video for reference purpose.
- every second, take a frame, save an image, this will be the main input for the model.

This is not the best solution, but it is the most practical solution for now.

There are several parameters you can specify when you start the video listener:

- `--api_domain`: the API domain, default is `http://localhost:8000`, which is within the full local setup
- `--token`: the token you get from the API side
- `--home_id`: If you use cloud mode, you can have multiple homes to upload video and audio data, as one of the most
  common user case for this could be home intelligent assistant. The home do not limit to an actual home, can be a
  hospital room, etc.

Then that's all, other setting if you want to customize, you can PR or change it by your own.

## Audio/Video/Image File Sync

We have described the STORAGE_SOLUTION in our [Deployment Options](../../Deployment/index.md)

The fastest way is definitely on the same machine for all modules, which actually is not practical in production.
So next option will be local network or cloud.

- local network, sync data to a center sever within home network
- cloud, upload to s3 or other cloud storage, then trigger the serverless function on cloud to download the file on a
  EFS, then AI and API should both mount to the EFS, this will reduce the 

