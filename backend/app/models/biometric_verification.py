import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VerificationStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"


class LivenessMethod(str, PyEnum):
    BLINK = "blink"
    SMILE = "smile"
    HEAD_TURN = "head_turn"
    RANDOM = "random"


class BiometricVerification(Base, TimestampMixin):
    __tablename__ = "biometric_verifications"
    __table_args__ = (
        Index("ix_biometric_verifications_student_status", "student_nim", "status"),
        Index("ix_biometric_verifications_challenge", "challenge_id"),
    )

    verification_id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"ver_{uuid.uuid4().hex[:12]}"
    )
    student_nim: Mapped[str] = mapped_column(
        String(20), ForeignKey("student_dpt.nim", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False
    )
    challenge_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # index challenge_id dibuat oleh Index eksplisit di __table_args__
    challenge_type: Mapped[LivenessMethod | None] = mapped_column(
        Enum(LivenessMethod), nullable=True
    )
    challenge_nonce: Mapped[str | None] = mapped_column(String(100), nullable=True)
    challenge_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    face_match_verified: Mapped[bool | None] = mapped_column(nullable=True)
    face_similarity: Mapped[float | None] = mapped_column(nullable=True)
    liveness_verified: Mapped[bool | None] = mapped_column(nullable=True)
    liveness_method: Mapped[LivenessMethod | None] = mapped_column(
        Enum(LivenessMethod), nullable=True
    )
    ai_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    student: Mapped["StudentDPT"] = relationship(
        "StudentDPT", back_populates="biometric_verifications"
    )

    def __repr__(self) -> str:
        return f"<BiometricVerification(id={self.verification_id}, student={self.student_nim}, status={self.status})>"

    @property
    def attempts_remaining(self) -> int:
        return max(0, self.max_attempts - self.attempts)

    @property
    def is_expired(self) -> bool:
        if self.challenge_expires_at:
            return datetime.now(timezone.utc) > self.challenge_expires_at
        return False

    @property
    def can_retry(self) -> bool:
        return self.attempts < self.max_attempts and not self.is_expired