from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from .change_file import ChangeFileResponse


class ChangeCreate(BaseModel):
    component_id: int
    title: str = Field(min_length=1, max_length=250)
    description: str = Field(min_length=1, max_length=1000)


class ChangeResponse(BaseModel):
    id: int
    change_number: int
    created_at: datetime
    last_modified_at: datetime
    project_id: int
    component_id: int
    ticket_id: int
    title: str
    description: str
    files: list[ChangeFileResponse]

    model_config = ConfigDict(from_attributes=True)

class ChangeUpdate(BaseModel):
    component_id: int | None = Field(ge=1, default=None)
    title: str | None = Field(min_length=1, max_length=250, default=None)
    description: str | None = Field(min_length=1, max_length=1000, default=None)



