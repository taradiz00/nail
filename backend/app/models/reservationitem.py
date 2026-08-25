from sqlalchemy import ForeignKey, Integer
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column



class ReservationItem(Base):
    __tablename__ = "reservation_item"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservation.id"),
        nullable=False,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id"),
        nullable=False,
    )

    deposit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )