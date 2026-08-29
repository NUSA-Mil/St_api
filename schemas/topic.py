from pydantic import BaseModel, ConfigDict


class TopicBase(BaseModel):
    subject_id: int
    name: str


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    subject_id: int | None = None
    name: str | None = None


class TopicResponse(TopicBase):
    id: int

    model_config = ConfigDict(from_attributes=True)