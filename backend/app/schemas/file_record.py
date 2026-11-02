from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

from datetime import datetime

class FileRecordResponse(BaseModel):
    id: int
    type_file: str = Field(min_length=1, max_length=30)
    original_name: str
    stored_name: str
    content_type: str
    size_bytes: int
    last_modified_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FileUploadMetadata(BaseModel):
    type_file: str = Field(min_length=1, max_length=30)
    role: Literal["before", "after", "attachment"] = "attachment"
    description: str = Field(min_length=1, max_length=1000)



