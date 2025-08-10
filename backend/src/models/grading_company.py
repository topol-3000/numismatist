from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .grade import Grade
    from .grading_info import GradingInfo


class GradingCompany(Base, UuidPkMixin):
    __tablename__ = "grading_companies"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cert_url_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    supported_types: Mapped[str] = mapped_column(String(100), nullable=False, default="coins")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    grading_info: Mapped[list["GradingInfo"]] = relationship(
        "GradingInfo",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    grades_list: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="noload",  # Prevent lazy loading issues in tests
    )

    @property
    def grades(self) -> dict[str, list[str]]:
        """Transform grades list into dictionary grouped by category."""
        if not self.grades_list:
            return {}

        grades_dict: dict[str, list[str]] = {}
        for grade in self.grades_list:
            if grade.category not in grades_dict:
                grades_dict[grade.category] = []
            grades_dict[grade.category].append(grade.value)

        # Sort grades within each category by sort_order
        for category in grades_dict:
            category_grades = [
                (grade.value, grade.sort_order) for grade in self.grades_list if grade.category == category
            ]
            category_grades.sort(key=lambda x: x[1])  # Sort by sort_order
            grades_dict[category] = [value for value, _ in category_grades]

        return grades_dict
