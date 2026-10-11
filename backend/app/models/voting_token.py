import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class TokenStatus(str, PyEnum):
    ISSUED = "issued"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class VotingToken(Base, TimestampMixin):
    __tablename__ = "voting_tokens"
    __table_args__ = (
        Index("ix_voting_tokens_student_status", "student_nim", "status"),
        Index("ix_voting_tokens_election", "election_id"),
        Index("ix_voting_tokens_token", "token_hash", unique=True),
    )

    token_id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"vt_{uuid.uuid4().hex[:12]}"
    )
    student_nim: Mapped[str] = mapped_column(
        String(20), ForeignKey("student_dpt.nim", ondelete="CASCADE"), nullable=False, index=True
    )
    election_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("elections.election_id", ondelete="CASCADE"), nullable=False, index=True
    )
    verification_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("biometric_verifications.verification_id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[TokenStatus] = mapped_column(
        Enum(TokenStatus), default=TokenStatus.ISSUED, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Relationships (optional, for admin queries)
    # student: Mapped["StudentDPT"] = relationship()
    # election: Mapped["Election"] = relationship()
    # verification: Mapped["BiometricVerification"] = relationship()

    def __repr__(self) -> str:
        return f"<VotingToken(id={self.token_id}, student={self.student_nim}, status={self.status})>"

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.status == TokenStatus.ISSUED and not self.is_expired