import hashlib
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Client,
    Reservation,
    PhoneVerification,
)
from app.schemas.phone_verif import VerificationConfirm


router = APIRouter(
    prefix="/verification",
    tags=["verification"],
)


def hash_code(code: str) -> str:
    return hashlib.sha256(
        code.encode()
    ).hexdigest()


@router.post("/send/{reservation_id}")
def send_verification_code(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id
        )
        .first()
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    client = (
        db.query(Client)
        .filter(
            Client.id == reservation.client_id
        )
        .first()
    )

    code = f"{random.randint(0, 999999):06d}"

    verification = PhoneVerification(
        phone=client.phone,
        code_hash=hash_code(code),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        attempts=0,
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    print("NEW VERIFICATION CREATED")
    print("ID:", verification.id)
    print("PHONE:", verification.phone)
    print("EXPIRES:", verification.expires_at)
    

    # TEMPORARY FOR DEVELOPMENT ONLY
    print("SMS CODE:", code)

    # Later:
    # sms_provider.send(
    #     phone=client.phone,
    #     message=f"کد تایید شما: {code}"
    # )

    return {
        "message": "Verification code sent"
    }




@router.post("/confirm")
def confirm_verification(
    data: VerificationConfirm,
    db: Session = Depends(get_db),
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == data.reservation_id
        )
        .first()
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    if (
        reservation.status == "pending"
        and reservation.hold_expires_at is not None
        and reservation.hold_expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=410,
            detail="Reservation hold has expired",
        )

    client = (
        db.query(Client)
        .filter(
            Client.id == reservation.client_id
        )
        .first()
    )
    

    all_verifications = (
        db.query(PhoneVerification)
        .order_by(PhoneVerification.id.desc())
        .all()
    ) 

    print("=== ALL VERIFICATIONS ===")

    for v in all_verifications:
        print(
            "ID:",
            v.id,
            "PHONE:",
            repr(v.phone),
            "USED:",
            v.used_at,
        )
    

    verification = (
        db.query(PhoneVerification)
        .filter(
            PhoneVerification.phone == client.phone,
            PhoneVerification.used_at.is_(None),
        )
        .order_by(
            PhoneVerification.id.desc()
        )
        .first()
    )

    if verification is None:
        raise HTTPException(
            status_code=400,
            detail="Verification code not found",
        )
    now = datetime.now(timezone.utc)

    print("========== VERIFICATION DEBUG ==========")
    print("Verification ID:", verification.id)
    print("Phone:", verification.phone)
    print("Expires at:", verification.expires_at)
    print("Expires timezone:", verification.expires_at.tzinfo)
    print("Current UTC:", now)
    print("Current timezone:", now.tzinfo)
    print("Difference:", verification.expires_at - now)
    print("========================================")

    if verification.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="Verification code expired",
        )

    if verification.attempts >= 5:
        raise HTTPException(
            status_code=400,
            detail="Too many attempts",
        )

    verification.attempts += 1

    entered_hash = hash_code(data.code)

    if entered_hash != verification.code_hash:
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid verification code",
        )

    verification.used_at = datetime.now()

    reservation.phone_verified = True

    

    db.commit()

    return {
        "verified": True,
        "reservation_id": reservation.id,
    }