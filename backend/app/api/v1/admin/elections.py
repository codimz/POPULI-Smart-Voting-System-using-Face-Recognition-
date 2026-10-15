from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.election import Election
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/admin/elections", tags=["Admin - Elections"])

@router.get("")
async def list_elections(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Election))
    return SuccessResponse(success=True, message="Elections", data=[{"id":e.election_id,"status":e.status.value} for e in result.scalars().all()], meta={"request_id":"t16"})