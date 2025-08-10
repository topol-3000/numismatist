from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .grading_company import GradingCompany
    from .item import Item


class GradingInfo(Base, UuidPkMixin):
    """
    Store third-party grading and certification information for collectible items.

    Links items to grading companies with certificate numbers and grade details.
    """

    __tablename__ = "grading_info"
    __table_args__ = (UniqueConstraint("item_id", name="uq_grading_info_item_id"),)

    item_id: Mapped[str] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("grading_companies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    certificate_number: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Unique certificate number from grading company"
    )
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Assigned grade (e.g., MS70, AU58)")
    grade_details: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Additional grade details (e.g., CLEANED, DAMAGED)"
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Additional notes about the grading")
    certificate_url: Mapped[str | None] = mapped_column(Text, nullable=True, comment="URL to verify certificate online")

    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="grading_info")
    company: Mapped["GradingCompany"] = relationship("GradingCompany", back_populates="grading_info")
