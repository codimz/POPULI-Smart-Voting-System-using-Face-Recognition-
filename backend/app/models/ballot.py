import uuid
from datetime import datetime, timezone
from sqlalchemy import UUID, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BallotBox(Base, TimestampMixin):
    __tablename__ = "ballot_box"
    __table_args__ = (
        UniqueConstraint("vote_hash", name="uq_vote_hash"),
    )

    ballot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidates.candidate_id", ondelete="RESTRICT"), nullable=False
    )
    election_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    casted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    vote_hash: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)

    # Relationships
    candidate: Mapped["Candidate"] = relationship(
        "Candidate", back_populates="ballots"
    )

    def __repr__(self) -> str:
        return f"<BallotBox(id={self.ballot_id}, candidate_id={self.candidate_id}, election={self.election_type})>"