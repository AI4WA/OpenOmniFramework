from pydantic import BaseModel, Field


class TaskData(BaseModel):
    task_name: str
    result_json: dict
    id: int
    parameters: dict
