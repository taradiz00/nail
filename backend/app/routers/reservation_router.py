from datetime import timedelta, datetime, timezone

from sqlalchemy import and_, or_ 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Client,
    Service,
    Reservation,
    ReservationItem,
    BlockedSlot,
)
from app.schemas.reservation_schema import ReservationCreate, ReservationResponse


router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
)


@router.post("/", response_model=ReservationResponse)
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
):
    if not data.service_ids:
        raise HTTPException(
            status_code=400,
            detail="No services selected",
        )

    unique_ids = set(data.service_ids)

    # Get services from PostgreSQL
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
            detail="Invalid service",
        )

    total_duration = sum(
        service.duration_minutes
        for service in services
    )

    end_at = data.start_at + timedelta(
        minutes=total_duration
    )

    # VERY IMPORTANT:
    # Check the time again.
    # Don't trust that it was still available
    # just because the calendar showed it earlier.

    now = datetime.now(timezone.utc)

    reservation_conflict = (
    db.query(Reservation)
    .filter(
        Reservation.start_at < end_at,
        Reservation.end_at > data.start_at,

        or_(
            Reservation.status == "confirmed",

            and_(
                Reservation.status == "pending",
                Reservation.hold_expires_at > now,
            ),
        ),
    )
    .first()
)

    if reservation_conflict:
        raise HTTPException(
            status_code=409,
            detail="This time is no longer available",
        )

    blocked_conflict = (
        db.query(BlockedSlot)
        .filter(
            BlockedSlot.start_at < end_at,
            BlockedSlot.end_at > data.start_at,
        )
        .first()
    )

    if blocked_conflict:
        raise HTTPException(
            status_code=409,
            detail="This time is unavailable",
        )

    # Find client by normalized phone
    client = (
        db.query(Client)
        .filter(Client.phone == data.phone)
        .first()
    )

    if client is None:
        client = Client(
            name=data.name,
            phone=data.phone,
            email=data.email,
        )

        db.add(client)

        # Gives us client.id without committing
        db.flush()

    else:
        # Optional: update latest information
        client.name = data.name

        if data.email is not None:
            client.email = data.email

    total_deposit = sum(
        service.deposit_amount
        for service in services
    )


    reservation = Reservation(
        client_id=client.id,
        start_at=data.start_at,
        end_at=end_at,
        status="pending",
        deposit_amount=total_deposit,
        phone_verified=False,
        hold_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(reservation)
    db.flush()

    for service in services:
        reservation_item = ReservationItem(
            reservation_id=reservation.id,
            service_id=service.id,
            deposit=service.deposit_amount,
        )

        db.add(reservation_item)

    db.commit()
    db.refresh(reservation)

    return reservation
