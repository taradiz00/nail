import logging

import httpx


from app.core.config import settings

from app.services.sms.base import (
    SMSProvider,
    SMSProviderError,
    SMSResult,
)


logger = logging.getLogger(__name__)


class FarazSMSProvider(SMSProvider):

    async def send_otp(
        self,
        phone: str,
        code: str,
    ) -> SMSResult:

        url = (
            f"{settings.FARAZSMS_BASE_URL.rstrip('/')}"
            "/sms/pattern"
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Api-Key": settings.FARAZSMS_API_KEY,
        }

        payload = {

            "code": settings.FARAZSMS_PATTERN_CODE,

            "attributes": {
                "code": code,
            },

            "recipient": phone,

            "line_number": settings.FARAZSMS_LINE_NUMBER,

            "number_format": "english",
        }

        try:

            async with httpx.AsyncClient(
                timeout=settings.SMS_TIMEOUT_SECONDS
            ) as client:

                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

        except httpx.TimeoutException as exc:

            logger.warning(
                "FarazSMS request timed out"
            )

            raise SMSProviderError(
                "SMS provider timed out"
            ) from exc

        except httpx.RequestError as exc:

            logger.warning(
                "FarazSMS connection error: %s",
                exc.__class__.__name__,
            )

            raise SMSProviderError(
                "SMS provider connection failed"
            ) from exc


        # FarazSMS pattern endpoint documents
        # HTTP 201 for successful creation/send.

        if response.status_code != 201:

            logger.warning(
                "FarazSMS returned HTTP %s",
                response.status_code,
            )

            raise SMSProviderError(
                f"SMS provider returned "
                f"HTTP {response.status_code}"
            )


        try:

            data = response.json()

        except ValueError as exc:

            logger.warning(
                "FarazSMS returned invalid JSON"
            )

            raise SMSProviderError(
                "Invalid response from SMS provider"
            ) from exc


        if data.get("status") != "success":

            logger.warning(
                "FarazSMS response was not successful"
            )

            raise SMSProviderError(
                "SMS provider rejected message"
            )


        provider_data = data.get("data")


        return SMSResult(
            provider_reference=(
                str(provider_data)
                if provider_data is not None
                else None
            )
        )