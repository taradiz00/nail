import hashlib
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import func

from sqlalchemy.orm import Session


from app.core.config import settings

from app.models import (
    Client,
    PhoneVerification,
    Reservation,
)

from app.services.sms.base import SMSProviderError

from app.services.sms.farazsms import (
    FarazSMSProvider,
)

# OTP EXCEPTIONS

class OTPError(Exception):
    pass


class OTPNotFoundError(OTPError):
    pass


class OTPExpiredError(OTPError):
    pass


class OTPInvalidError(OTPError):
    pass


class OTPTooManyAttemptsError(OTPError):
    pass


class OTPDeliveryError(OTPError):
    pass


class OTPRateLimitError(OTPError):

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
    ):

        super().__init__(message)

        self.retry_after = retry_after


# OTP SERVICE


class OTPService:

    def __init__(self):

        self.sms_provider = FarazSMSProvider()

    # TIME

    @staticmethod
    def _now() -> datetime:

        return datetime.now(
            timezone.utc
        )

    # GENERATE OTP

    @staticmethod
    def _generate_code() -> str:

        return (
            f"{secrets.randbelow(1_000_000):06d}"
        )


    # HASH OTP

    @staticmethod
    def _hash_code(
        code: str,
    ) -> str:

        return hashlib.sha256(
            code.encode("utf-8")
        ).hexdigest()

    # RATE LIMITS

    def _check_send_limits(
        self,
        db: Session,
        reservation: Reservation,
        phone: str,
        request_ip: str | None,
        now: datetime,
    ) -> None:

        # --------------------------
        # 60 SECOND RESEND COOLDOWN
        # --------------------------

        last_sent = (
            db.query(PhoneVerification)
            .filter(
                PhoneVerification.reservation_id
                == reservation.id,

                PhoneVerification.status
                == "sent",

                PhoneVerification.sent_at.is_not(
                    None
                ),
            )
            .order_by(
                PhoneVerification.sent_at.desc()
            )
            .first()
        )


        if (
            last_sent is not None
            and last_sent.sent_at is not None
        ):

            elapsed = (
                now - last_sent.sent_at
            ).total_seconds()


            if elapsed < settings.OTP_RESEND_SECONDS:

                retry_after = max(
                    1,
                    int(
                        settings.OTP_RESEND_SECONDS
                        - elapsed
                    ),
                )

                raise OTPRateLimitError(
                    "Please wait before requesting "
                    "another verification code.",
                    retry_after=retry_after,
                )


        # --------------------------
        # LAST HOUR
        # --------------------------

        hour_ago = (
            now - timedelta(hours=1)
        )


        # --------------------------
        # LIMIT PER RESERVATION
        # --------------------------

        reservation_count = (
            db.query(
                func.count(
                    PhoneVerification.id
                )
            )
            .filter(
                PhoneVerification.reservation_id
                == reservation.id,

                PhoneVerification.created_at
                >= hour_ago,
            )
            .scalar()
            or 0
        )


        if (
            reservation_count
            >= settings
            .OTP_MAX_SENDS_PER_HOUR_RESERVATION
        ):

            raise OTPRateLimitError(
                "Too many verification codes "
                "requested for this reservation."
            )


        # --------------------------
        # LIMIT PER PHONE
        # --------------------------

        phone_count = (
            db.query(
                func.count(
                    PhoneVerification.id
                )
            )
            .filter(
                PhoneVerification.phone
                == phone,

                PhoneVerification.created_at
                >= hour_ago,
            )
            .scalar()
            or 0
        )


        if (
            phone_count
            >= settings
            .OTP_MAX_SENDS_PER_HOUR_PHONE
        ):

            raise OTPRateLimitError(
                "Too many verification codes "
                "requested for this phone number."
            )


        # --------------------------
        # LIMIT PER IP
        # --------------------------

        if request_ip:

            ip_count = (
                db.query(
                    func.count(
                        PhoneVerification.id
                    )
                )
                .filter(
                    PhoneVerification.request_ip
                    == request_ip,

                    PhoneVerification.created_at
                    >= hour_ago,
                )
                .scalar()
                or 0
            )


            if (
                ip_count
                >= settings
                .OTP_MAX_SENDS_PER_HOUR_IP
            ):

                raise OTPRateLimitError(
                    "Too many verification-code "
                    "requests."
                )


    # ==========================
    # SEND OTP
    # ==========================

    async def send_code(
        self,
        db: Session,
        reservation: Reservation,
        client: Client,
        request_ip: str | None,
    ) -> PhoneVerification:

        now = self._now()


        # --------------------------
        # ALREADY VERIFIED
        # --------------------------

        if reservation.phone_verified:

            raise OTPError(
                "Phone number is already verified."
            )


        # --------------------------
        # RESERVATION STATUS
        # --------------------------

        if reservation.status != "pending":

            raise OTPError(
                "Reservation cannot be verified."
            )


        # --------------------------
        # RESERVATION HOLD
        # --------------------------

        if (
            reservation.hold_expires_at
            is not None

            and reservation.hold_expires_at
            <= now
        ):

            raise OTPExpiredError(
                "Reservation hold has expired."
            )


        # --------------------------
        # RATE LIMIT
        # --------------------------

        self._check_send_limits(
            db=db,
            reservation=reservation,
            phone=client.phone,
            request_ip=request_ip,
            now=now,
        )


        # --------------------------
        # GENERATE SECURE CODE
        # --------------------------

        code = self._generate_code()


        # --------------------------
        # CREATE DB RECORD
        # --------------------------

        verification = PhoneVerification(

            reservation_id=reservation.id,

            phone=client.phone,

            code_hash=self._hash_code(
                code
            ),

            expires_at=(
                now
                + timedelta(
                    minutes=
                    settings.OTP_EXPIRY_MINUTES
                )
            ),

            attempts=0,

            status="pending",

            provider="farazsms",

            request_ip=request_ip,

            created_at=now,
        )


        db.add(
            verification
        )

        db.commit()

        db.refresh(
            verification
        )


        # --------------------------
        # SEND TO FARAZ SMS
        # --------------------------

        try:

            result = (
                await self
                .sms_provider
                .send_otp(
                    phone=client.phone,
                    code=code,
                )
            )


        except SMSProviderError as exc:

            verification.status = (
                "failed"
            )

            verification.failure_reason = (
                str(exc)[:500]
            )

            db.commit()


            raise OTPDeliveryError(
                "Unable to send verification "
                "code. Please try again."
            ) from exc


        # --------------------------
        # SMS ACCEPTED
        # --------------------------

        sent_at = self._now()


        # --------------------------
        # INVALIDATE OLD CODES
        # --------------------------

        previous_codes = (
            db.query(
                PhoneVerification
            )
            .filter(
                PhoneVerification.reservation_id
                == reservation.id,

                PhoneVerification.id
                != verification.id,

                PhoneVerification.status
                == "sent",

                PhoneVerification.used_at.is_(
                    None
                ),
            )
            .all()
        )


        for previous in previous_codes:

            previous.status = (
                "invalidated"
            )

            previous.used_at = sent_at


        # --------------------------
        # MARK NEW OTP SENT
        # --------------------------

        verification.status = "sent"

        verification.sent_at = sent_at

        verification.provider_message_id = (
            result.provider_reference
        )


        db.commit()

        db.refresh(
            verification
        )


        return verification


    # ==========================
    # VERIFY OTP
    # ==========================

    def verify_code(
        self,
        db: Session,
        reservation: Reservation,
        code: str,
    ) -> PhoneVerification | None:

        # --------------------------
        # ALREADY VERIFIED
        # --------------------------

        if reservation.phone_verified:

            return None


        now = self._now()


        # --------------------------
        # RESERVATION HOLD
        # --------------------------

        if (
            reservation.status == "pending"

            and reservation.hold_expires_at
            is not None

            and reservation.hold_expires_at
            <= now
        ):

            raise OTPExpiredError(
                "Reservation hold has expired."
            )


        # --------------------------
        # GET ACTIVE OTP
        # --------------------------

        verification = (
            db.query(
                PhoneVerification
            )
            .filter(
                PhoneVerification.reservation_id
                == reservation.id,

                PhoneVerification.status
                == "sent",

                PhoneVerification.used_at.is_(
                    None
                ),
            )
            .order_by(
                PhoneVerification.id.desc()
            )
            .with_for_update()
            .first()
        )


        if verification is None:

            raise OTPNotFoundError(
                "No valid verification code "
                "found. Please request a new code."
            )


        # --------------------------
        # EXPIRED
        # --------------------------

        if (
            verification.expires_at
            <= now
        ):

            verification.status = (
                "expired"
            )

            db.commit()


            raise OTPExpiredError(
                "Verification code has expired. "
                "Please request a new code."
            )


        # --------------------------
        # MAX ATTEMPTS
        # --------------------------

        if (
            verification.attempts
            >= settings.OTP_MAX_ATTEMPTS
        ):

            verification.status = (
                "locked"
            )

            verification.used_at = now

            db.commit()


            raise OTPTooManyAttemptsError(
                "Too many incorrect attempts. "
                "Please request a new code."
            )


        # --------------------------
        # COUNT ATTEMPT
        # --------------------------

        verification.attempts += 1


        # --------------------------
        # HASH ENTERED CODE
        # --------------------------

        entered_hash = (
            self._hash_code(
                code
            )
        )


        matches = secrets.compare_digest(
            entered_hash,
            verification.code_hash,
        )


        # --------------------------
        # WRONG CODE
        # --------------------------

        if not matches:

            if (
                verification.attempts
                >= settings.OTP_MAX_ATTEMPTS
            ):

                verification.status = (
                    "locked"
                )

                verification.used_at = now


            db.commit()


            raise OTPInvalidError(
                "Invalid verification code."
            )


        # --------------------------
        # SUCCESS
        # --------------------------

        verification.status = (
            "verified"
        )

        verification.used_at = now


        reservation.phone_verified = (
            True
        )


        db.commit()

        db.refresh(
            verification
        )


        return verification


otp_service = OTPService()