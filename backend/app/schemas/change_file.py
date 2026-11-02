from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from .file_record import FileRecordResponse


class ChangeFileCreate(BaseModel):
    role: Literal["before", "after", "attachment"] = "attachment"
    description: str = Field(min_length=1)


class ChangeFileResponse(BaseModel):
    id: int
    change_id: int
    file_id: int
    role: Literal["before", "after", "attachment"]
    description: str
    
    file: FileRecordResponse

    model_config = ConfigDict(from_attributes=True)
