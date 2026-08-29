from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from models.topic import Topic
    from models.exam_variant import ExamVariant


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связи с аннотацией типов
    topics: Mapped[list["Topic"]] = relationship(
        "Topic", back_populates="subject", cascade="all, delete-orphan"
    )
    exam_variants: Mapped[list["ExamVariant"]] = relationship(
        "ExamVariant", back_populates="subject", cascade="all, delete-orphan"
    )