from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ElectionStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Election(Base, TimestampMixin):
    __tablename__ = "elections"
    __table_args__ = (
        Index("ix_elections_status", "status"),
        Index("ix_elections_type", "election_type"),
    )

    election_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    election_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ElectionStatus] = mapped_column(
        Enum(ElectionStatus), default=ElectionStatus.DRAFT, nullable=False
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registration_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Election(id={self.election_id}, type={self.election_type}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.status == ElectionStatus.ACTIVE and self.starts_at <= now <= self.ends_at

    @property
    def is_registration_open(self) -> bool:
        if not self.registration_starts_at or not self.registration_ends_at:
            return False
        now = datetime.now(timezone.utc)
        return self.registration_starts_at <= now <= self.registration_ends_at