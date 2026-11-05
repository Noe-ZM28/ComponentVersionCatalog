from pydantic import BaseModel, ConfigDict, Field


class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)
    cadena: str
    step: int = Field(ge=1)
    ref_id: str | None = Field(default=None, min_length=1, max_length=100)
    source_type: str = Field(min_length=1, max_length=30, default="other")
    source_reference: str | None = Field(min_length=1, default=None)

class ComponentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str
    cadena: str
    step: int
    ref_id: str | None = Field(default=None)
    source_type: str
    source_reference: str | None = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
