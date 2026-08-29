from typing import Any
from pydantic import BaseModel, ConfigDict
from models.task import AnswerType


class TaskBase(BaseModel):
    topic_id: int
    task_number: int
    question_text: str
    answer_type: AnswerType
    correct_answers: Any
    explanation: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    topic_id: int | None = None
    task_number: int | None = None
    question_text: str | None = None
    answer_type: AnswerType | None = None
    correct_answers: Any | None = None
    explanation: str | None = None


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TaskCheckRequest(BaseModel):
        user_answer: Any  # Строка, число или список ответов

class TaskCheckResponse(BaseModel):
        is_correct: bool
        message: str
        explanation: str | None = None