from pydantic import BaseModel, ConfigDict
from typing import Any
from schemas.task import TaskResponse


class ExamVariantBase(BaseModel):
    subject_id: int
    title: str


class ExamVariantCreate(ExamVariantBase):
    pass


class ExamVariantUpdate(BaseModel):
    subject_id: int | None = None
    title: str | None = None


class ExamVariantResponse(ExamVariantBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Новые схемы для сдачи экзамена ---

class TaskWithOrderResponse(TaskResponse):
    order: int


class VariantTaskAnswer(BaseModel):
    task_id: int
    user_answer: Any


class SubmitExamRequest(BaseModel):
    answers: list[VariantTaskAnswer]


class TaskCheckResult(BaseModel):
    task_id: int
    user_answer: Any
    is_correct: bool
    correct_answers: Any
    explanation: str | None = None


class SubmitExamResponse(BaseModel):
    variant_id: int
    total_tasks: int
    correct_count: int
    score_percentage: float
    results: list[TaskCheckResult]