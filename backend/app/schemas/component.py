from pydantic import BaseModel, ConfigDict, Field


class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)
    cadena: str
    step: int = Field(ge=1)


class ComponentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str
    cadena: str
    step: int

    model_config = ConfigDict(from_attributes=True)
