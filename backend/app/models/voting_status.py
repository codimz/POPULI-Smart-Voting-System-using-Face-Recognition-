from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VotingStatus(Base, TimestampMixin):
    __tablename__ = "voting_status"

    nim: Mapped[str] = mapped_column(
        String(20), ForeignKey("student_dpt.nim", ondelete="CASCADE"), primary_key=True
    )
    has_voted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    voted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_method: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    # Relationships
    student: Mapped["StudentDPT"] = relationship(
        "StudentDPT", back_populates="voting_status"
    )

    def __repr__(self) -> str:
        return f"<VotingStatus(nim={self.nim}, has_voted={self.has_voted})>"