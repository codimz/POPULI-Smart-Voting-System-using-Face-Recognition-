# T18: Audit logging service (minimal)
from datetime import datetime
from typing import Optional
from app.core.database import AsyncSession
from app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    async def log(
        session: AsyncSession,
        event_type: str,
        student_nim: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
    ):
        # Larangan log: password, JWT, raw image, embedding, pilihan kandidat
        audit = AuditLog(
            event_type=event_type,
            student_nim=student_nim,
            ip_address=ip_address,
            details=details,
            created_at=datetime.utcnow(),
        )
        session.add(audit)
        await session.commit()
