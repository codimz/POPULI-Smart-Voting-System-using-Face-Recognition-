from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.vote_engine import get_vote_engine
from app.models.student import StudentDPT
from app.schemas.common import SuccessResponse
from app.schemas.admin import DashboardStats
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/admin/dashboard", tags=["Admin - Dashboard"])


@router.get("", response_model=SuccessResponse[DashboardStats])
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Admin dashboard stats."""
    vote_engine = get_vote_engine(db)
    turnout = await vote_engine.get_turnout_stats()
    stats = DashboardStats(
        total_voters=turnout.get("total_voters", 0),
        voted_count=turnout.get("voted_count", 0),
        turnout_percentage=turnout.get("turnout_percentage", 0.0),
        total_candidates=0,
        active_elections=1,
        pending_verifications=0,
    )
    return SuccessResponse(success=True, message="Dashboard berhasil.", data=stats, meta={"request_id": "req_dash"})