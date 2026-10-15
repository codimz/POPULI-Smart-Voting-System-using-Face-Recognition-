from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/admin/reports/export", tags=["Admin - Reports"])

@router.get("/csv")
async def export_csv(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    return SuccessResponse(success=True, message="CSV export (placeholder)", data={"format":"csv","url":"/reports/export.csv"}, meta={"request_id":"t19"})