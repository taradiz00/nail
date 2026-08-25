from sqlalchemy import String, DateTime
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta, timezone


class PhoneVerification(Base):
    __tablename__ = "phone_verification"

    id: Mapped[int] = mapped_column(primary_key=True)

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    now = datetime.now(timezone.utc)

    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), nullable=False)

    used_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)

    hold_expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), nullable=True)

    attempts: Mapped[int] = mapped_column(
        default=0,
    )