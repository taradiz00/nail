from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from app.core.database import Base


class PhoneVerification(Base):
    __tablename__ = "phone_verification"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # RESERVATION

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reservation.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # PHONE

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    # OTP

    code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # SEND INFORMATION

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # pending / sent / verified /
    # invalidated / expired / locked / failed

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True,
    )

    # PROVIDER
    

    provider: Mapped[str] = mapped_column(
        String(30),
        default="farazsms",
        nullable=False,
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # RATE LIMITING

    request_ip: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )