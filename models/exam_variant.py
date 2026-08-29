from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from models.subject import Subject
    from models.variant_task import VariantTask


class ExamVariant(Base):
    __tablename__ = "exam_variants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связи с аннотацией типов
    subject: Mapped["Subject"] = relationship("Subject", back_populates="exam_variants")
    task_links: Mapped[list["VariantTask"]] = relationship(
        "VariantTask", back_populates="variant", cascade="all, delete-orphan"
    )