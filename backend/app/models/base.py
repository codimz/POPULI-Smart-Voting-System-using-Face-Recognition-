from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

# Base didefinisikan sekali di core.database agar metadata tercampur
# (mencegah init_db() membuat tabel kosong karena Base terpisah).
from app.core.database import Base

__all__ = ["Base", "TimestampMixin"]


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )