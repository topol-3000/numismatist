from typing import Annotated

from pydantic import Field, field_validator

from schemas.base import SchemaConfigMixin


class GradingCompanyBasic(SchemaConfigMixin):
    """Basic grading company info with only essential fields."""

    id: Annotated[str, Field(description="ID of the grading company")]
    short_name: Annotated[str, Field(max_length=20, description="Short name or abbreviation")]


class GradingInfoBase(SchemaConfigMixin):
    """Base schema for grading info with core fields and validation."""

    company_id: Annotated[str, Field(description="ID of the grading company")]
    certificate_number: Annotated[str, Field(min_length=1, max_length=64, description="Certificate number")]
    grade: Annotated[str | None, Field(max_length=32, description="Grade value")] = None
    grade_details: Annotated[str | None, Field(max_length=64, description="Grade details")] = None
    note: Annotated[str | None, Field(max_length=255, description="Additional note")] = None
    certificate_url: Annotated[str | None, Field(max_length=255, description="Certificate URL")] = None

    @field_validator("certificate_number")
    @classmethod
    def validate_certificate_number(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Certificate number cannot be empty")

        return v.strip()


class GradingInfoCreate(SchemaConfigMixin):
    """Schema for creating a new grading info entry."""

    company_id: Annotated[str, Field(description="ID of the grading company")]
    certificate_number: Annotated[str, Field(min_length=1, max_length=64, description="Certificate number")]
    grade: Annotated[str | None, Field(max_length=32, description="Grade value")] = None
    grade_details: Annotated[str | None, Field(max_length=64, description="Grade details")] = None
    note: Annotated[str | None, Field(max_length=255, description="Additional note")] = None
    certificate_url: Annotated[str | None, Field(max_length=255, description="Certificate URL")] = None

    @field_validator("certificate_number")
    @classmethod
    def validate_certificate_number(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Certificate number cannot be empty")
        return v.strip()


class GradingInfoUpdate(SchemaConfigMixin):
    """Schema for updating grading info entries."""

    company_id: Annotated[str | None, Field(description="ID of the grading company")] = None
    certificate_number: Annotated[str | None, Field(min_length=1, max_length=64, description="Certificate number")] = (
        None
    )
    grade: Annotated[str | None, Field(max_length=32, description="Grade value")] = None
    grade_details: Annotated[str | None, Field(max_length=64, description="Grade details")] = None
    note: Annotated[str | None, Field(max_length=255, description="Additional note")] = None
    certificate_url: Annotated[str | None, Field(max_length=255, description="Certificate URL")] = None


class GradingInfoRead(GradingInfoBase):
    """Schema for reading grading info entries."""

    id: Annotated[str, Field(description="ID of the grading info")]
    item_id: Annotated[str, Field(description="ID of the item")]
    company: Annotated[GradingCompanyBasic | None, Field(description="Grading company")] = None
