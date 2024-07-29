# Video Demo

## Scripts

Notes: Here we will use the architecture diagram to explain the scripts.

Hello everyone, excited to introduce your our latest work, multimodal Open Source Conversational AI Framework: OpenOmni
Framework.

Why We build this comes from these points:

- It is approachable to build an end-to-end conversational AI system now with current models and tools available.
- However, if someone want to try out, they will need to speed quite a lot of time to get it work from scratch.
- And we do not know whether the latency and accuracy is acceptable or not.

So To make sure people do not re-invent the wheel, we build this framework, for details, you can check our
documentations.

Here what we will demo is one of the useful scenario for the framework, use conversational AI to help visually impaired
people to navigate indoors.

Notes: Here video will show the three devices, one is the AI module, one is the API module, and one is the client
module.

We will use the local network deployment option, deploy AI/API/Client modules within three different devices within the
same network.

So the audio, and video data will be collected from this raspberry pi, and then sync to the API server, together with
the metadata.

Then the API end will base on the parameters, allocate the task for the AI module, AI will then process the task. For
example, speech2text, llm generation, text2speech.

All the computational heavy work will happen here.

When the results are finished, the data or generated audio will be sent back to the API side

And the client side will have another thread to list to the API side, and then play the audio, fulfill the conversation.

Note: then next is the demo.

Ok, let's start the audio collection process, all other modules are currently running now.

Hi, where is my cup of coffee, can you tell me how to grab it?

Notes: Then wait for the response, and then play the audio.

After this finished, as a research or benchmark process.

Note: show the API interface here.

You will directly get the latency details and summary stats from our API interface.

We can see how long each module takes, and in total how long it takes to finish the whole process, which part are the
model inference time, which part is data transfer time.

Also, we can annotate and benchmark the accuracy of the process, whether the response tones, content is fit for the
scenario.

After the annotation, you will be able to see the details and summaries in this page.

This can be powerful for the conversational AI system research and application development, you can use this evaluate
different combination of pipeline.

Gathering datasets, etc.

Hopefully this can benefit the wider community, and we are looking forward to your feedback.