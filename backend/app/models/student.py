from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class StudentDPT(Base, TimestampMixin):
    __tablename__ = "student_dpt"

    nim: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    study_program: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    face_embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    voting_status: Mapped["VotingStatus"] = relationship(
        "VotingStatus", back_populates="student", uselist=False
    )
    biometric_verifications: Mapped[list["BiometricVerification"]] = relationship(
        "BiometricVerification", back_populates="student"
    )

    def __repr__(self) -> str:
        return f"<StudentDPT(nim={self.nim}, name={self.full_name}, registered={self.is_registered})>"