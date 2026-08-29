from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from models.subject import Subject
    from models.material import Material
    from models.task import Task


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связи с аннотацией типов
    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    materials: Mapped[list["Material"]] = relationship(
        "Material", back_populates="topic", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="topic", cascade="all, delete-orphan"
    )