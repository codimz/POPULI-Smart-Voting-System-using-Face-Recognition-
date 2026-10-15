from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.vote_engine import get_vote_engine
from app.schemas.admin import ElectionResultResponse, ResultData
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/admin/analytics/results", tags=["Admin - Results"])

@router.get("", response_model=SuccessResponse[list[ResultData]])
async def election_results(
    election_id: str = "el_active",
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    engine = get_vote_engine(db)
    results = await engine.get_results(election_id)
    return SuccessResponse(success=True, message="Hasil berhasil.", data=results, meta={"request_id":"req_t15"})