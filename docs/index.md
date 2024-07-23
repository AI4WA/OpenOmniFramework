# OpenOmni Framework

## How OpenAI GPT-4o works?

![./docs/images/GPT-4o.jpg](./images/GPT-4o.jpg)

## How traditional conversational AI?

![./docs/images/OpenOmni.jpg](./images/OpenOmni.jpg)

For an end to end conversational AI system, currently, there are mainly two approaches:

- Right side is what we think OpenAI GPT-4o is doing.
- Left side is what traditional conversational AI is doing.

As demonstrated in their video, OpenAI is working on an end-to-end model, which is quite impressive and theoretically
state-of-the-art.

However, there are challenges:

- We do not know how they implement it or why they can achieve such results.
- Fully end-to-end models are difficult to implement because most researchers lack the resources
  (**money** and **data**) to train such models.

To reach the level of OpenAI, we need:

1. **Collaborative Efforts**: Crowd efforts where everyone focuses on advancing their own part without reinventing the
   wheel.
2. **High Agility**: A process that allows people to easily test their models, understand real application issues, and
   improve them.
3. **Gathering Data**: More data to advance system development, especially for complex conversational scenarios. This
   includes understanding who is talking, the context, and the emotion, which is lacking in current datasets.

To address these needs, we are building **OpenBenang**, a system that:

- Allows people to easily test their models, whether end-to-end or single components within the pipeline.
- Can be easily deployed, enabling researchers to collect the data they need with minimal effort for adaptation.

Our ultimate goal is to:

- Develop an open-source, end-to-end conversational AI robot that match the capabilities of OpenAI's GPT-4o.
- Enable easy data collection for advancing the development of end-to-end conversational AI systems.
- Inspire and foster the development of innovative conversational AI applications and products.

## System Operation Overview

1. **Data Collection:** Video and audio inputs are collected from hardware devices.
2. **Data Transfer:** Data is sent to the API for downstream processing.
3. **Data Processing:** The API uses AI and ML models to process the data, generate responses.
4. **Reaction:** The client side is notified to play the speech.

There are two key metrics we are focusing on:

- **Model Latency:** The time it takes for the model to generate a response.
- **Model Accuracy:** Whether the model generates the in-context response or accurate response.

In the end we will want to respond to the user's query in a timely manner, and provide the most in-context response.

---

## Architecture

![Architecture](./images/ArchitectureDesign.jpg)

---

## Main Components

From Application Development Perspective, we divide the whole applications into three main components:

- Client
- API
- AI

### Client

Detailed information can be found in [Client](Client/main.md).

Client is decoupled from the API, to reduce the complexity of the system, and allow researchers or developers easily
integrate their own model into the system.

The client side will mainly in charge of

- Data Acquisition
    - Audio
    - Video
- Data Transfer
    - Transfer the data to storage places
- Data Presentation
    - Play the speech

### API

Detailed information can be found in [API](./API.md).

This is the **Brain** of the system, which will be in charge of:

- Knowledge Base
    - Relational Database
    - Graph Database
- Models Orchestration
    - LLM
    - GPT-4 API
    - Self-developed models
- API Interface
    - RESTful API
    - WebSocket API
- Data Management

### AI

Detailed information can be found in [AI](./AI.md).

- Running the ML or AI models
    - Running the models which require intensive computation
    - LLM models
    - Text2Speech models
    - Emotion Recognition models
    - etc.

The API side will work as the orchestrator, to manage the models, and provide the interface for the client to access


---
