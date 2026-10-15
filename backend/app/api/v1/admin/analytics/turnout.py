from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.student import StudentDPT
from app.schemas.admin import TurnoutByProgram
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter(prefix="/admin/analytics/turnout", tags=["Admin - Turnout"])

@router.get("", response_model=SuccessResponse[list[TurnoutByProgram]])
async def turnout_breakdown(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(StudentDPT.study_program, func.count(StudentDPT.nim)).group_by(StudentDPT.study_program)
    )
    data = [TurnoutByProgram(study_program=row[0], total_voters=row[1], voted_count=0, turnout_percentage=0.0) for row in result.all()]
    return SuccessResponse(success=True, message="Turnout berhasil.", data=data, meta={"request_id":"req_t14"})