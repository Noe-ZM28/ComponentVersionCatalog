from pydantic import BaseModel, Field, ConfigDict
from .component import ComponentResponse


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    components: list[ComponentResponse]

    model_config = ConfigDict(from_attributes=True)
