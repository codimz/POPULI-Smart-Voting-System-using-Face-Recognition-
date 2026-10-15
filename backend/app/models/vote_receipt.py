import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Index, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VoteReceipt(Base, TimestampMixin):
    __tablename__ = "vote_receipts"
    __table_args__ = (
        Index("ix_vote_receipts_student", "student_nim"),
        Index("ix_vote_receipts_election", "election_id"),
        Index("ix_vote_receipts_vote_hash", "vote_hash"),
    )

    receipt_id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"rcpt_{uuid.uuid4().hex[:12]}"
    )
    student_nim: Mapped[str] = mapped_column(
        String(20), ForeignKey("student_dpt.nim", ondelete="CASCADE"), nullable=False, index=True
    )
    election_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("elections.election_id", ondelete="CASCADE"), nullable=False, index=True
    )
    vote_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ballot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ballot_box.ballot_id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<VoteReceipt(id={self.receipt_id}, student={self.student_nim}, election={self.election_id})>"