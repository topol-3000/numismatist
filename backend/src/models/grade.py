from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .grading_company import GradingCompany


class Grade(Base, UuidPkMixin):
    __tablename__ = "grades"

    company_id: Mapped[str] = mapped_column(ForeignKey("grading_companies.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Grading system: modern, ancient, details"
    )
    value: Mapped[str] = mapped_column(String(50), nullable=False, comment="Grade value (MS 70, Ch XF, CLEANED, etc.)")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Display order within category")

    company: Mapped["GradingCompany"] = relationship("GradingCompany", back_populates="grades_list")
