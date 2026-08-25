from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Service,
    Reservation,
    BlockedSlot,
    WorkingHours,
)
from app.schemas.availability_schema import AvailabilityRequest, AvailabilityResponse

router = APIRouter(
    prefix="/availability",
    tags=["availability"],
)


@router.post("/", response_model=AvailabilityResponse)
def get_available_times(
    data: AvailabilityRequest,
    db: Session = Depends(get_db),
):
    if not data.service_ids:
        raise HTTPException(
            status_code=400,
            detail="No services selected",
        )
    
    unique_ids = set(data.service_ids)

    services = (
        db.query(Service)
        .filter(
            Service.id.in_(unique_ids),
            Service.is_active.is_(True),
        )
        .all()
    )

    if len(services) != len(unique_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more services are invalid",
        )

    total_duration = sum(
        service.duration_minutes
        for service in services
    )

    weekday = data.date.weekday()

    working_hours = (
        db.query(WorkingHours)
        .filter(WorkingHours.weekday == weekday)
        .first()
    )

    if working_hours is None:
        return AvailabilityResponse(
            date=data.date,
            total_duration_minutes=total_duration,
            available_times=[],
        )

    opening = datetime.combine(
        data.date,
        working_hours.start_time,
    )

    closing = datetime.combine(
        data.date,
        working_hours.end_time,
    )

    day_start = datetime.combine(
        data.date,
        datetime.min.time(),
    )

    day_end = day_start + timedelta(days=1)

    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.start_at < day_end,
            Reservation.end_at > day_start,
            Reservation.status.in_(
                ["pending", "confirmed"]
            ),
        )
        .all()
    )

    blocked_slots = (
        db.query(BlockedSlot)
        .filter(
            BlockedSlot.start_at < day_end,
            BlockedSlot.end_at > day_start,
        )
        .all()
    )


    available_times = []

    # Allow starts every 30 minutes
    interval = timedelta(minutes=30)

    duration = timedelta(
        minutes=total_duration
    )

    current_start = opening

    while current_start + duration <= closing:
        current_end = current_start + duration

        reservation_conflict = any(
            current_start < reservation.end_at
            and current_end > reservation.start_at
            for reservation in reservations
        )

        blocked_conflict = any(
            current_start < blocked.end_at
            and current_end > blocked.start_at
            for blocked in blocked_slots
        )

        if not reservation_conflict and not blocked_conflict:
            available_times.append(
                current_start.strftime("%H:%M")
            )

        current_start += interval

    return AvailabilityResponse(
        date=data.date,
        total_duration_minutes=total_duration,
        available_times=available_times,
    )
