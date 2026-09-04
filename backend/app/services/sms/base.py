from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SMSResult:
    provider_reference: str | None = None


class SMSProviderError(Exception):
    pass


class SMSProvider(ABC):

    @abstractmethod
    async def send_pattern(
        self,
        phone: str,
        pattern_code: str,
        attributes: dict[str, str],
    ) -> SMSResult:

        raise NotImplementedError


    @abstractmethod
    async def send_otp(
        self,
        phone: str,
        code: str,
    ) -> SMSResult:

        raise NotImplementedError