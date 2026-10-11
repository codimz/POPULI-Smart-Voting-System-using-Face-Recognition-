from datetime import datetime, timezone
from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class IdempotencyRecord(Base, TimestampMixin):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_idempotency_key"),
        # index expires_at dibuat otomatis lewat index=True pada kolom
    )

    idempotency_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    response_status: Mapped[int | None] = mapped_column(nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<IdempotencyRecord(key={self.idempotency_key}, expires={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at