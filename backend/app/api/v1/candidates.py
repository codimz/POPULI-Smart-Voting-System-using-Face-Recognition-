from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_student
from app.models.candidate import Candidate
from app.models.election import Election, ElectionStatus
from app.schemas.candidate import CandidateResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("", response_model=SuccessResponse[List[CandidateResponse]])
async def list_candidates(
    election_type: Optional[str] = Query(None, description="Filter by election"),
    db: AsyncSession = Depends(get_db),
    student=Depends(get_current_student),
):
    """Public candidate list for voters."""
    query = select(Candidate)
    if election_type:
        # Check if active election exists
        query = query.where(Candidate.election_type == election_type)
    result = await db.execute(query)
    candidates = result.scalars().all()

    data = [
        CandidateResponse(
            candidate_id=c.candidate_id,
            candidate_name=c.candidate_name,
            study_program=c.study_program,
            vision=c.vision,
            election_type=c.election_type,
            created_at=c.created_at.isoformat() if c.created_at else None,
        )
        for c in candidates
    ]
    return SuccessResponse(success=True, message="Kandidat berhasil diambil.", data=data, meta={"request_id": "req_public"})