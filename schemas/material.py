from pydantic import BaseModel, ConfigDict


class MaterialBase(BaseModel):
    topic_id: int
    title: str
    content: str


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    topic_id: int | None = None
    title: str | None = None
    content: str | None = None


class MaterialResponse(MaterialBase):
    id: int

    model_config = ConfigDict(from_attributes=True)