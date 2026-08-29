from pydantic import BaseModel, ConfigDict


class SubjectBase(BaseModel):
    name: str


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = None


class SubjectResponse(SubjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)