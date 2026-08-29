from pydantic import BaseModel, ConfigDict


class VariantTaskBase(BaseModel):
    variant_id: int
    task_id: int
    order: int


class VariantTaskCreate(VariantTaskBase):
    pass


class VariantTaskUpdate(BaseModel):
    order: int | None = None


class VariantTaskResponse(VariantTaskBase):
    model_config = ConfigDict(from_attributes=True)