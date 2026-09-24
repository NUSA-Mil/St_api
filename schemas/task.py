from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from models.task import AnswerType


class TaskBase(BaseModel):
    topic_id: int
    task_number: int
    question_text: str
    answer_type: AnswerType
    correct_answers: Any
    explanation: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    topic_id: Optional[int] = None
    task_number: Optional[int] = None
    question_text: Optional[str] = None
    answer_type: Optional[AnswerType] = None
    correct_answers: Optional[Any] = None
    explanation: Optional[str] = None


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskCheckRequest(BaseModel):
    user_answer: Any


class TaskCheckResponse(BaseModel):
    is_correct: bool
    correct_answers: Optional[Any] = None
    message: str
    explanation: Optional[str] = None