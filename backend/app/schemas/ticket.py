from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TicketCreate(BaseModel):
    project_id: int 
    title: str = Field(min_length=1, max_length=250)
    description : str = Field(min_length=1, max_length=1000)
    ticket_url: str = Field(min_length=1, max_length = 500)

class TicketResponse(BaseModel):
    id: int
    ticket_key: str
    title: str
    description: str
    ticket_url: str
    registered_at: datetime
    #changes: list[ComponentResponse]

    model_config = ConfigDict(from_attributes=True)
