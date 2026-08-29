from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from models.exam_variant import ExamVariant
    from models.task import Task


class VariantTask(Base):
    __tablename__ = "variant_tasks"

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("exam_variants.id", ondelete="CASCADE"), primary_key=True
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    order: Mapped[int] = mapped_column("order", nullable=False)

    # Связи с аннотацией типов
    variant: Mapped["ExamVariant"] = relationship("ExamVariant", back_populates="task_links")
    task: Mapped["Task"] = relationship("Task", back_populates="variant_links")