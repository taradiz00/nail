from sqlalchemy import Integer, Time
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time

class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(primary_key=True)

    weekday: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
