import enum
from typing import Any, TYPE_CHECKING
from sqlalchemy import Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from models.topic import Topic
    from models.variant_task import VariantTask


class AnswerType(str, enum.Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"
    MATCHING = "matching"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    task_number: Mapped[int] = mapped_column(nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[AnswerType] = mapped_column(
        Enum(
            AnswerType,
            name="answer_type",
            create_type=False,
            values_callable=lambda x: [e.value for e in x]  # Сохраняет 'single' вместо 'SINGLE'
        ),
        nullable=False
    )
    correct_answers: Mapped[Any] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связи
    topic: Mapped["Topic"] = relationship("Topic", back_populates="tasks")
    variant_links: Mapped[list["VariantTask"]] = relationship(
        "VariantTask", back_populates="task", cascade="all, delete-orphan"
    )