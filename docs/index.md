# OpenOmni Framework

Multimodal Open Source Framework for Conversational AI Research and Development.

----

- [Motivation](#motivation)
- [Approaches](#approaches)
    - [Traditional conversational AI](#traditional-conversational-ai)
    - [OpenAI GPT-4o](#openai-gpt-4o)
    - [Hybrid Approach](#hybrid-approach)
    - [Summary](#summary)
- [Our System Design](#how-traditional-conversational-ai)
    - [Requirements](#requirements)
    - [System Architecture](#system-architecture)
    - [Main Components](#main-components)
        - [Client](#client)
        - [API](#api)
        - [AI](#ai)
- [Key Features](#key-features)
- [Tutorial](#tutorial)
- [How to Deploy](#how-to-deploy)

----

## Motivation

The development of Multimodal Large Language Models (LLMs) is opening new frontiers in conversational AI research and
applications. Multimodal end-to-end conversational AI represents a significant advancement in our pursuit of general AI.
This progress, however, is not without its challenges. Balancing cost, accuracy, and latency remains a difficult task.

<div style="text-align: center;">
  <img src="./images/Triangle.jpg" alt="OpenOmni" width="300"/>
</div>


GPT-4 has demonstrated the capability of a fully end-to-end multimodal model to handle complex multimodal inputs,
including audio and images, and generate coherent and contextually appropriate responses in a timely manner. Compared to
traditional approaches such as speech-to-text, text generation, and text-to-speech, which suffer from latency issues
that hinder their real-world applicability, GPT-4 has shown the potential to overcome these challenges. This showcases
the potential of advanced AI models to navigate the rough path towards a bright future in conversational AI.

Despite these advancements, achieving the right balance between cost, accuracy, and latency is a significant hurdle.
This difficulty is the motivation behind our project. We aim to establish an open-source framework that allows
researchers to easily test their contributions and collaborate effectively. By doing so, we hope to facilitate the
research and development process, accelerating the journey towards more efficient and capable multimodal conversational
AI systems.

----

## Approaches

- Traditional approach is to **Divide and Conquer**, however it suffers from the latency issue
- GPT-4o is **End-to-End** model, which is different from the traditional approach, and overcome the latency issue.
  However, it is hard to implement for wider community.
- Other approaches is **Hybrid** Approach, an end to end voice model, which take audio and texts as input, and generate
  audio as output. Video modality input can be converted to text, and then feed into the model.

### Traditional conversational AI

![./docs/images/OpenOmni.jpg](./images/OpenOmni.jpg)

The whole pipeline divided into several components, mainly including:

- Speech2Text
- Information Retrieval (Text based or Video based)
- Text Generation
- Text2Speech

Before the era of LLM, Speech2Text and Text2Speech tasks are the most successful ones, delivering quite a few successful
products.
However, generate in-context response is a challenging task, which is a bottleneck for
the whole pipeline, which is the **Accuracy** issue.
Development of LLMs solves this problem directly.

However, it is still one more problem, which is the **Latency** issue, before it can really impact the real world
seriously.

### OpenAI GPT-4o

![./docs/images/GPT-4o.jpg](./images/GPT-4o.jpg)

Demonstration from OpenAI indicates that they have achieved acceptable **Latency** performance, which is around 250ms.
At the same time, the **Accuracy** is also impressive, according to their released
benchmark: [GPT-4o Benchmark](https://openai.com/index/hello-gpt-4o/).

However, we noticed that there is a cable connected to the iPhone when they are doing the demonstration, and it is
described to maintain stable and high speed internet connection.
Which means, reasonable latency is achievable, however, not yet scalable to the real world.
The delay of public release of GPT-4o with audio and video ability proves this point to some extent.
Our testing with current GPT-4o endpoints indicates even the fastest pipeline combination with OpenAI API (
Whisper,GPT-3.5,OpenAI TTS) still have 5-8 seconds latency.

### Hybrid Approach

![./docs/images/VoiceE2E.jpg](./images/VoiceE2E.jpg)

Unlike GPT-4o, with audio, video, or/and text as input, which is challenging to implement, some researchers are
exploring a hybrid approach, which is to take audio and/or text as input, and generate audio and/or text as output.

[Moshi](https://moshi.chat/?queue_id=talktoMoshi) is one of the examples.
Images and Videos normally are very large, and require a lot of computation power to process, this approaches
can overcome this issue.
Another advantage of this is that without take the video as input, it avoids the privacy issue, act not like a "Big
Brother is Watch you", potentially is more acceptable by the public.

### Summary

The research focus for multimodal conversational AI is shifting towards end-to-end models, however, it is a **money**
game.
To achieve that, you will need intelligent people (which we have in research community), data, and money.
Data and money is not evenly distributed within the research community, which makes the wider research community hard to
catch up with the cutting edge research.

Sadly to say that, but reality is the rest research community without enough data and money can work towards the
direction: adopt and applying conversational AI the into the real world, and make it more accessible to the public.
Contributing to the bigger picture as a small piece of the puzzle.

This leads to the development and goal of OpenOmni Framework Project.

1. **Collaborative Efforts**: Crowd efforts where everyone focuses on advancing their own part without reinventing the
   wheel.
2. **High Agility**: A process that allows people to easily test their models, understand real application issues, and
   improve them.
3. **Gathering Data**: More data to advance system development, especially for complex conversational scenarios. This
   includes understanding who is talking, the context, and the emotion, which is lacking in current datasets.

We want to:

- Allows people to easily test their models, whether end-to-end or single components within the pipeline.
- Can be easily deployed, enabling researchers to collect the data they need with minimal effort for adaptation.

Our ultimate goal is to:

- Develop an open-source, end-to-end conversational AI robot that match the capabilities of OpenAI's GPT-4o.
- Enable easy data collection for advancing the development of end-to-end conversational AI systems.
- Inspire and foster the development of innovative conversational AI applications and products.

---

## System Design

### Requirements

What the functions we need from the system perspective:

1. **Data Collection:** Video and audio inputs are collected from hardware devices.
2. **Data Transfer:** Data is sent to the API for downstream processing.
3. **Data Processing:** The API uses AI and ML models to process the data, generate responses.
4. **Reaction:** The client side is notified to play the speech.

There are two key metrics we are focusing on:

- **Model Latency:** The time it takes for the model to generate a response.
- **Model Accuracy:** Whether the model generates the in-context response or accurate response.

Which will allow to react to user's query in a timely manner, and provide the most in-context response.

### System Architecture

![Architecture](./images/ArchitectureDesign.jpg)

### Main Components

So as you can see from the system architecture, we have three main components: **Client**, **API**, and **AI**.

Client will be in charge of data acquisition, and data presentation.
Which means the video and audio data will be collected from the client side, and the speech generated by the AI will be
played by the client side.

API will be the orchestrator, which will manage the models, and provide the API interface for the Client/AI module to
access.
It also provides the access and CURD to the data sources (Neo4j, PostgreSQL and Hard Disk).
It also includes an interface for end users (Researchers and Annotators) to interact with the system.

AI module is seperated to make sure it can be scaled to use different computation resources, and easily to integrate new
work in.

#### Client

Detailed information can be found in [Client](Client/main.md).

The client side will mainly in charge of

- Data Acquisition
    - Audio
    - Video
- Data Transfer
    - Transfer the data to storage places
- Data Presentation
    - Play the speech

#### API

Detailed information can be found in [API](./API.md).

This is the **Brain** of the system, which will be in charge of:

- Knowledge Base
    - Relational Database
    - Graph Database
    - Hard Disk
- Models Orchestration
    - LLM
    - GPT-4 API
    - Self-developed models
- API Interface
    - RESTful API
- Data Management with an Admin interface
- Annotation Interface for the annotators
- Benchmark report for the researchers

#### AI

Detailed information can be found in [AI](./AI.md).

- Running the ML or AI models
    - Running the models which require intensive computation
    - LLM models
    - Text2Speech models
    - Emotion Recognition models
    - etc.

---

## Key Features

