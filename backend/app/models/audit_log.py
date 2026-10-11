from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_event_type_timestamp", "event_type", "timestamp"),
        Index("ix_audit_logs_ip_address", "ip_address"),
    )

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.log_id}, event={self.event_type}, timestamp={self.timestamp})>"