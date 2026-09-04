from sqlalchemy import String, DateTime, func, ForeignKey, Integer, Boolean
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class Reservation(Base):
    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id"),
        nullable=False,
    )

    start_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    end_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    total_price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    deposit_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
        )

    client: Mapped["Client"] = relationship(
        back_populates="reservations"
    )

    hold_expires_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,)

    client_confirmation_sms_sent_at: Mapped[
    datetime | None
] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)


admin_confirmation_sms_sent_at: Mapped[
    datetime | None
] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)