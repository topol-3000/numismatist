from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin


class GradingCompanyBase(SchemaConfigMixin):
    """Base schema for grading company data."""

    name: Annotated[str, Field(description="Full name of the grading company")]
    short_name: Annotated[str, Field(max_length=20, description="Short name or abbreviation")]
    country: Annotated[str | None, Field(max_length=100, description="Country")] = None
    website: Annotated[str | None, Field(max_length=255, description="Website URL")] = None
    cert_url_pattern: Annotated[str | None, Field(max_length=255, description="Certificate URL pattern")] = None
    supported_types: Annotated[str, Field(description="Supported item types")] = "coins"
    is_active: Annotated[bool, Field(description="Is company active")] = True
    grades: Annotated[dict[str, list[str]] | None, Field(description="Available grades by category")] = None


class GradingCompanyCreate(GradingCompanyBase):
    """Schema for creating a new grading company."""


class GradingCompanyUpdate(SchemaConfigMixin):
    """Schema for updating grading company data."""

    name: Annotated[str | None, Field(description="Full name of the grading company")] = None
    short_name: Annotated[str | None, Field(max_length=20, description="Short name or abbreviation")] = None
    country: Annotated[str | None, Field(max_length=100, description="Country")] = None
    website: Annotated[str | None, Field(max_length=255, description="Website URL")] = None
    cert_url_pattern: Annotated[str | None, Field(max_length=255, description="Certificate URL pattern")] = None
    supported_types: Annotated[str | None, Field(description="Supported item types")] = None
    is_active: Annotated[bool | None, Field(description="Is company active")] = None
    grades: Annotated[dict[str, list[str]] | None, Field(description="Available grades by category")] = None


class GradingCompanyRead(GradingCompanyBase):
    """Schema for reading grading company data."""

    id: Annotated[str, Field(description="ID of the grading company")]
