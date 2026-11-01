from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .change import ChangeResponse, ChangeCreate


class TicketCreate(BaseModel):
    ticket_key: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=250)
    description : str = Field(min_length=1, max_length=1000)
    ticket_url: str = Field(min_length=1, max_length = 500)
    changes: list[ChangeCreate] = Field(min_length=1)

class TicketResponse(BaseModel):
    id: int
    ticket_key: str
    title: str
    description: str
    ticket_url: str
    registered_at: datetime
    changes: list[ChangeResponse]

    model_config = ConfigDict(from_attributes=True)

class TicketUpdate(BaseModel):
    ticket_key: str | None = Field(min_length=1, max_length=100, default=None)
    title: str | None = Field(min_length=1, max_length=250, default=None)
    description : str | None = Field(min_length=1, max_length=1000, default=None)
    ticket_url: str | None = Field(min_length=1, max_length = 500, default=None)




