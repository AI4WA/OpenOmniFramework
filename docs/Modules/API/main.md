# API

API will provide the central logic control and orchestration for the whole system.
It is written in Django and Django Rest Framework.
The database is PostgresSQL.

The apps in the API are [continue to be developed]:

- authenticate:
    - User authentication
    - JWT token generation
    - API token generation
- hardware:
    - Hardware management
    - Store audio and video data
    - Store the artifacts of the pipeline
- llm:
    - Manage the configuration of the LLM models
- orchestrator:
    - Manage the pipeline
    - Queue the tasks
    - Manage the pipeline hooks

Currently, it will provide the following functionalities:

- admin interface: http://localhost:8000/
- API docs: http://localhost:8000/redoc

If you want to add any new functionalities, it is quite easy, you just need to know how to use Django.

## Data Storage

- We have a relational database, which is PostgresSQL.
- For the audio and video data, we will store them in the file system.
- We also include the Neo4j for future development of GraphRAG.
