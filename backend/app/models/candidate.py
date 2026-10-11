from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("election_type", "candidate_name", name="uq_election_candidate"),
    )

    candidate_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    election_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    candidate_name: Mapped[str] = mapped_column(String(100), nullable=False)
    vision_mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    ballots: Mapped[list["BallotBox"]] = relationship(
        "BallotBox", back_populates="candidate"
    )

    def __repr__(self) -> str:
        return f"<Candidate(id={self.candidate_id}, name={self.candidate_name}, election={self.election_type})>"