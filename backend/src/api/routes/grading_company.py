from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from models import GradingCompany
from schemas.grading_company import GradingCompanyCreate, GradingCompanyRead, GradingCompanyUpdate

router = APIRouter(prefix="/grading-companies", tags=["Grading Companies"])


@router.get("/{company_id}/grades", response_model=dict[str, list[str]])
async def get_company_grades(
    company_id: str,
    session: SessionDependency,
):
    """Get all supported grades for a specific grading company, grouped by category."""
    result: Result[Any] = await session.execute(
        select(GradingCompany).options(selectinload(GradingCompany.grades_list)).where(GradingCompany.id == company_id)
    )
    company: GradingCompany | None = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grading company not found")

    return company.grades


@router.get("/{company_id}", response_model=GradingCompanyRead)
async def get_grading_company(
    company_id: str,
    session: SessionDependency,
):
    """Get grading company by ID."""
    result: Result[Any] = await session.execute(
        select(GradingCompany).options(selectinload(GradingCompany.grades_list)).where(GradingCompany.id == company_id)
    )
    company: GradingCompany | None = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grading company not found")

    return company


@router.get("/", response_model=list[GradingCompanyRead])
async def list_grading_companies(session: SessionDependency):
    """List all active grading companies."""
    result: Result[Any] = await session.execute(
        select(GradingCompany)
        .options(selectinload(GradingCompany.grades_list))
        .where(GradingCompany.is_active)
        .order_by(GradingCompany.name)
    )
    companies: list[GradingCompany] = list(result.scalars().all())
    return companies


@router.post("/", response_model=GradingCompanyRead, status_code=status.HTTP_201_CREATED)
async def create_grading_company(
    company_data: GradingCompanyCreate,
    session: SessionDependency,
):
    """Create a new grading company."""
    company = GradingCompany(**company_data.model_dump())
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


@router.patch("/{company_id}", response_model=GradingCompanyRead)
async def update_grading_company(
    company_id: str,
    company_data: GradingCompanyUpdate,
    session: SessionDependency,
):
    """Update a grading company."""
    result: Result[Any] = await session.execute(select(GradingCompany).where(GradingCompany.id == company_id))
    company: GradingCompany | None = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grading company not found")

    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    await session.commit()
    await session.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grading_company(
    company_id: str,
    session: SessionDependency,
):
    """Delete a grading company."""
    result: Result[Any] = await session.execute(select(GradingCompany).where(GradingCompany.id == company_id))
    company: GradingCompany | None = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grading company not found")

    await session.delete(company)
    await session.commit()
