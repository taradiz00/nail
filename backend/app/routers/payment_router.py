from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from datetime import datetime
from app.models import Reservation
from app.schemas import PaymentRequest


router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("/start")
def start_payment(
    data: PaymentRequest,
    db: Session = Depends(get_db),
):
    reservation = (
        db.query(Reservation)
        .filter(Reservation.id == data.reservation_id)
        .first()
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    if not reservation.phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Phone must be verified first",
        )

    if reservation.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Reservation cannot be paid",
        )

    if (
        reservation.hold_expires_at is not None
        and reservation.hold_expires_at <= datetime.now()
    ):
        raise HTTPException(
            status_code=410,
            detail="Reservation hold has expired",
        )

    amount = reservation.deposit_amount

    return {
        "reservation_id": reservation.id,
        "amount": amount,
        "message": "Ready for payment gateway",
    }