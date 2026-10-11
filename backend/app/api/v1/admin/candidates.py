from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
)
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter(prefix="/admin/candidates", tags=["Admin - Candidates"])


@router.post(
    "",
    response_model=SuccessResponse[CandidateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Create a new candidate."""
    candidate = Candidate(**candidate_data.model_dump())
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return SuccessResponse(
        success=True,
        message="Kandidat berhasil dibuat.",
        data=CandidateResponse.model_validate(candidate),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.get(
    "",
    response_model=PaginatedResponse[CandidateResponse],
    status_code=status.HTTP_200_OK,
)
async def list_candidates(
    election_type: Optional[str] = Query(None, description="Filter by election type"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """List candidates with pagination."""
    query = select(Candidate)
    if election_type:
        query = query.where(Candidate.election_type == election_type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Paginate
    query = query.order_by(Candidate.candidate_id).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    candidates = result.scalars().all()

    return PaginatedResponse(
        success=True,
        message="Daftar kandidat berhasil diambil.",
        data=[CandidateResponse.model_validate(c) for c in candidates],
        meta={
            "page": page,
            "size": size,
            "total": total,
            "total_pages": (total + size - 1) // size,
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
        },
    )


@router.get(
    "/{candidate_id}",
    response_model=SuccessResponse[CandidateResponse],
    status_code=status.HTTP_200_OK,
)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Get candidate by ID."""
    result = await db.execute(
        select(Candidate).where(Candidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kandidat tidak ditemukan",
        )

    return SuccessResponse(
        success=True,
        message="Data kandidat berhasil diambil.",
        data=CandidateResponse.model_validate(candidate),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.patch(
    "/{candidate_id}",
    response_model=SuccessResponse[CandidateResponse],
    status_code=status.HTTP_200_OK,
)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Update candidate."""
    result = await db.execute(
        select(Candidate).where(Candidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kandidat tidak ditemukan",
        )

    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)

    return SuccessResponse(
        success=True,
        message="Kandidat berhasil diperbarui.",
        data=CandidateResponse.model_validate(candidate),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.delete(
    "/{candidate_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Delete candidate."""
    result = await db.execute(
        select(Candidate).where(Candidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kandidat tidak ditemukan",
        )

    await db.delete(candidate)
    await db.commit()

    return SuccessResponse(
        success=True,
        message="Kandidat berhasil dihapus.",
        data=None,
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


import uuid