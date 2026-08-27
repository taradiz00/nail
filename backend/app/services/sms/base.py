from abc import ABC, abstractmethod

from dataclasses import dataclass


@dataclass(frozen=True)
class SMSResult:

    provider_reference: str | None = None


class SMSProviderError(Exception):
    """
    Raised when the SMS provider cannot
    successfully accept an SMS request.
    """

    pass


class SMSProvider(ABC):

    @abstractmethod
    async def send_otp(
        self,
        phone: str,
        code: str,
    ) -> SMSResult:

        raise NotImplementedError