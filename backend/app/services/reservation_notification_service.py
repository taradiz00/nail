import logging

from datetime import (
    datetime,
    timezone,
)

import jdatetime

from sqlalchemy.orm import Session


from app.core.config import settings

from app.models import (
    Client,
    Reservation,
)

from app.services.sms.base import (
    SMSProviderError,
)

from app.services.sms.farazsms import (
    FarazSMSProvider,
)


logger = logging.getLogger(__name__)


class ReservationNotificationService:

    def __init__(self):

        self.sms_provider = FarazSMSProvider()


    # ==========================
    # FORMAT JALALI DATE
    # ==========================

    @staticmethod
    def _format_date(
        value: datetime,
    ) -> str:

        jalali = (
            jdatetime.datetime
            .fromgregorian(
                datetime=value
            )
        )

        return jalali.strftime(
            "%Y/%m/%d"
        )


    # ==========================
    # FORMAT TIME
    # ==========================

    @staticmethod
    def _format_time(
        value: datetime,
    ) -> str:

        return value.strftime(
            "%H:%M"
        )


    # ==========================
    # CLIENT SMS
    # ==========================

    async def send_client_confirmation(
        self,
        db: Session,
        reservation: Reservation,
        client: Client,
    ) -> bool:

        # Already sent
        if (
            reservation
            .client_confirmation_sms_sent_at
            is not None
        ):

            return True


        attributes = {

            "name":
                client.name,

            "date":
                self._format_date(
                    reservation.start_at
                ),

            "time":
                self._format_time(
                    reservation.start_at
                ),

            "booking_id":
                str(reservation.id),
        }


        try:

            await self.sms_provider.send_pattern(

                phone=client.phone,

                pattern_code=(
                    settings
                    .FARAZSMS_CLIENT_CONFIRMATION_PATTERN
                ),

                attributes=attributes,
            )


        except SMSProviderError as exc:

            logger.error(
                "Client confirmation SMS failed "
                "for reservation %s: %s",
                reservation.id,
                exc,
            )

            return False


        reservation.client_confirmation_sms_sent_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        return True


    # ==========================
    # ADMIN SMS
    # ==========================

    async def send_admin_confirmation(
        self,
        db: Session,
        reservation: Reservation,
        client: Client,
    ) -> bool:

        # Already sent
        if (
            reservation
            .admin_confirmation_sms_sent_at
            is not None
        ):

            return True


        attributes = {

            "name":
                client.name,

            "phone":
                client.phone,

            "date":
                self._format_date(
                    reservation.start_at
                ),

            "time":
                self._format_time(
                    reservation.start_at
                ),

            "booking_id":
                str(reservation.id),
        }


        try:

            await self.sms_provider.send_pattern(

                phone=settings.ADMIN_PHONE,

                pattern_code=(
                    settings
                    .FARAZSMS_ADMIN_CONFIRMATION_PATTERN
                ),

                attributes=attributes,
            )


        except SMSProviderError as exc:

            logger.error(
                "Admin confirmation SMS failed "
                "for reservation %s: %s",
                reservation.id,
                exc,
            )

            return False


        reservation.admin_confirmation_sms_sent_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        return True


    # ==========================
    # SEND BOTH
    # ==========================

    async def send_confirmation_messages(
        self,
        db: Session,
        reservation: Reservation,
        client: Client,
    ) -> dict[str, bool]:

        client_sent = (
            await self.send_client_confirmation(
                db=db,
                reservation=reservation,
                client=client,
            )
        )


        admin_sent = (
            await self.send_admin_confirmation(
                db=db,
                reservation=reservation,
                client=client,
            )
        )


        return {
            "client_sms_sent":
                client_sent,

            "admin_sms_sent":
                admin_sent,
        }


reservation_notification_service = (
    ReservationNotificationService()
)