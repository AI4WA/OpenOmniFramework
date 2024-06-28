# API

API will provide the central logic control and orchestration for the whole system.
It is written in Django and Django Rest Framework.
The database is PostgresSQL.

The apps in the API are [continue to be developed:

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
- Hasura and hasura_management:
    - Hasura GraphQL API
    - Hasura management
    - This one will provide a GraphQL API to the PostgresSQL database for rapid development

Currently, it will provide the following functionalities:

- admin interface: http://localhost:8000/
- API docs: http://localhost:8000/redoc
- Swagger: http://localhost:8000/swagger

## Hasura

Within the API codebase, we also have a standalone Hasura instance running, which is used to
provide a GraphQL API to the PostgresSQL database.

## Authentication and Authorization

Within the whole APP, everyone should belong to one of the organizations, organization can be from industry
or research.

Each organization can have multiple users.
Among the users, there are different roles, such as:

- org_admin
- org_editor
- org_viewer

