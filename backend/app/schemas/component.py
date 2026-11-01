from pydantic import BaseModel, ConfigDict, Field


class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    cadena: str | None = None
    step: str | None = None


class ComponentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None
    cadena: str | None
    step: str | None

    model_config = ConfigDict(from_attributes=True)
