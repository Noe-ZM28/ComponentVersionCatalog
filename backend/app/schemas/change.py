from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ChangeCreate(BaseModel):
    component_id: int
    title: str = Field(min_length=1, max_length=250)
    description: str = Field(min_length=1)


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
    cadena: str
    step: int

    model_config = ConfigDict(from_attributes=True)
