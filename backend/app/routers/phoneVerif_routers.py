from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from sqlalchemy.orm import Session


from app.core.database import get_db

from app.models import (
    Client,
    Reservation,
)

from app.schemas.phone_verif import VerificationConfirm


from app.services.otp_services import (
    OTPDeliveryError,
    OTPError,
    OTPExpiredError,
    OTPInvalidError,
    OTPNotFoundError,
    OTPRateLimitError,
    OTPTooManyAttemptsError,
    otp_service,
)


router = APIRouter(
    prefix="/verification",
    tags=["verification"],
)


# ==========================
# GET RESERVATION
# ==========================


def get_reservation_or_404(
    db: Session,
    reservation_id: int,
) -> Reservation:

    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id
            == reservation_id
        )
        .first()
    )


    if reservation is None:

        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )


    return reservation


# ==========================
# GET CLIENT
# ==========================


def get_client_or_404(
    db: Session,
    reservation: Reservation,
) -> Client:

    client = (
        db.query(Client)
        .filter(
            Client.id
            == reservation.client_id
        )
        .first()
    )


    if client is None:

        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )


    return client


# ==========================
# SEND VERIFICATION CODE
# ==========================


@router.post(
    "/send/{reservation_id}"
)
async def send_verification_code(
    reservation_id: int,
    request: Request,
    db: Session = Depends(get_db),
):

    reservation = (
        get_reservation_or_404(
            db,
            reservation_id,
        )
    )


    client = (
        get_client_or_404(
            db,
            reservation,
        )
    )


    request_ip = (
        request.client.host
        if request.client
        else None
    )


    try:

        verification = (
            await otp_service.send_code(
                db=db,
                reservation=reservation,
                client=client,
                request_ip=request_ip,
            )
        )


    # ==========================
    # RATE LIMIT
    # ==========================

    except OTPRateLimitError as exc:

        headers = {}


        if exc.retry_after is not None:

            headers[
                "Retry-After"
            ] = str(
                exc.retry_after
            )


        raise HTTPException(
            status_code=
            status.HTTP_429_TOO_MANY_REQUESTS,

            detail=str(exc),

            headers=headers,
        ) from exc


    # ==========================
    # EXPIRED RESERVATION
    # ==========================

    except OTPExpiredError as exc:

        raise HTTPException(
            status_code=
            status.HTTP_410_GONE,

            detail=str(exc),
        ) from exc


    # ==========================
    # SMS PROVIDER FAILURE
    # ==========================

    except OTPDeliveryError as exc:

        raise HTTPException(
            status_code=
            status.HTTP_503_SERVICE_UNAVAILABLE,

            detail=str(exc),
        ) from exc


    # ==========================
    # OTHER OTP ERROR
    # ==========================

    except OTPError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    return {

        "sent": True,

        "verification_id":
            verification.id,

        "expires_in_seconds":
            60 * 5,
    }


# ==========================
# CONFIRM VERIFICATION CODE
# ==========================


@router.post(
    "/confirm"
)
def confirm_verification(
    data: VerificationConfirm,
    db: Session = Depends(get_db),
):

    reservation = (
        get_reservation_or_404(
            db,
            data.reservation_id,
        )
    )


    # ==========================
    # VALIDATE FORMAT
    # ==========================

    if (
        len(data.code) != 6
        or not data.code.isdigit()
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Verification code must "
                "contain exactly 6 digits."
            ),
        )


    try:

        otp_service.verify_code(
            db=db,
            reservation=reservation,
            code=data.code,
        )


    except OTPNotFoundError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    except OTPExpiredError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    except OTPTooManyAttemptsError as exc:

        raise HTTPException(
            status_code=429,
            detail=str(exc),
        ) from exc


    except OTPInvalidError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    return {

        "verified": True,

        "reservation_id":
            reservation.id,
    }