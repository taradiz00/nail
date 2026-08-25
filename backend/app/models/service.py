from sqlalchemy import String, Integer, Boolean
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Service(Base):
    __tablename__ = "service"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    category: Mapped[str] = mapped_column(String(30), nullable=False)

    deposit_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )