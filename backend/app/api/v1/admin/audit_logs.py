from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter(prefix="/admin/audit-logs", tags=["Admin - Audit"])

@router.get("")
async def audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return SuccessResponse(success=True, message="Audit logs (placeholder)", data={"page":page,"per_page":per_page,"items":[]}, meta={"request_id":"t17"})