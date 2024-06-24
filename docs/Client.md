# Client

We have several client side processes that are used to interact with end users and API.

For the **INPUT** functionalities, we have:

- Audio Acquisition
- Video Acquisition
- File Sync

For the **OUTPUT** functionalities, we have:

- Text to Speech

We have two interfaces with the API:

- API interface to communicate the metadata of the audio and video.
- File Sync to sync the files to the server.

## Input Functionalities

### Audio Acquisition

The end of the goal is to transcribe the audio to text.
There are several ways we can implement it.
Ideally, we want the audio to be transcribed in real-time.
But we do not have the expertise to do it, so we choose to use Whisper[OpenAI] to do the transcription.
The whole process will be divided into two steps:

- Detect when the user stops speaking the sentence.
- Translate the audio from last stop to the current stop to text.

Due to the limitation performance of the Raspberry Pi, the latency of the transcription on the Raspberry Pi is not
acceptable.
So we choose to use the client to send the audio to the server, and the server will do the transcription.
Because the server has a better performance than the Raspberry Pi.

So our current solution is in the order of:

1. The client will detect whether the user stops speaking.
2. If so, output the audio to a `.wav` file. At the same time, call the API to create this audio record.
3. file sync process will sync the audio to the server through local internet via `rsync`.
4. The server will do the transcription from the `.wav` file, and update the record in the database.
5. This then will become a signal to **trigger** the emotion detection process.

#### Challenges

- Balancing between latency and accuracy.
- If multiple users in the scene, how to distinguish the audio from different users.
- How to detect the user stops speaking, or we should try other ways to control this?

### Video Acquisition

For now, the video acquisition is straightforward; we save the images in a defined sampling rate.
And the video also will be saved also for further analysis in the future.
The files will be synced to the server through the file sync process, same as the audio.

When emotion detection is triggered, the relevant images will be retrieved based on some defined rules.

#### Challenges

- The challenges will from the model side, if we decide that we will also use the image information to determine who is
  speaking. Then we need to redesign the whole workflow.
- The Main thing to consider is when we retrieve the images, how to retrieve the images that are relevant to the audio.

### File Sync

The model in the end (including the emotion detection models, LLM and Whisper) will be running on the local server
within the home network.
It is not practical to run the model on the Raspberry Pi.

We can explore the possibility of running the model on an Nvidia Jetson Nano, but it is not the focus for now.
To ensure the latency of the model, we will sync the files to the server through the local network, which is rapid.

#### Challenges

- We Need to do the evaluation on the latency of the file sync process.

## Output Functionalities

Currently, LLM will be augmented with the emotion detection model output, and then respond to the text user provided.
Ideally, we want to be able to convert the text to a speech with

- natural voice [If possible, use voice cloning]
- emotion included

However, it is hard to achieve this goal.

So the main functions here are:

- Text to Speech
- Sync speech information from the server to the client [If needed]
- Play the audio

Currently, what we have done is:

1. Client will have a process to keep checking whether there is a new text to be spoken.
2. If so, the client will convert the text to speech with gTTS.
3. The audio will be played.

#### Challenges

- How to make the voice more natural.
- How to include the emotion in the voice.
- How to make the voice more human-like, for example, the voice will be the same as his/her son/daughter.

