from typing import Optional

from pydantic import BaseModel, Field


class TaskData(BaseModel):
    task_name: str
    result_json: dict
    id: int
    parameters: dict
    track_id: Optional[str] = Field(None, description="The track id of the task")
    user_id: Optional[int] = Field(None, description="The user id of the task")
