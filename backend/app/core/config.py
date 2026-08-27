from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # ==========================
    # DATABASE
    # ==========================

    DATABASE_URL: str


    # ==========================
    # FARAZ SMS
    # ==========================

    FARAZSMS_API_KEY: str

    FARAZSMS_PATTERN_CODE: str

    FARAZSMS_LINE_NUMBER: str

    FARAZSMS_BASE_URL: str = (
        "https://api.iranpayamak.com/ws/v1"
    )


    # ==========================
    # OTP
    # ==========================

    OTP_EXPIRY_MINUTES: int = 5

    OTP_MAX_ATTEMPTS: int = 5

    OTP_RESEND_SECONDS: int = 60

    OTP_MAX_SENDS_PER_HOUR_RESERVATION: int = 5

    OTP_MAX_SENDS_PER_HOUR_PHONE: int = 5

    OTP_MAX_SENDS_PER_HOUR_IP: int = 10


    # ==========================
    # SMS HTTP SETTINGS
    # ==========================

    SMS_TIMEOUT_SECONDS: float = 10.0


    # ==========================
    # EMAIL
    # ==========================
    # Optional for now.
    # When email functionality is implemented,
    # put the real values in .env.

    EMAIL_ADDRESS: str | None = None

    EMAIL_PASSWORD: str | None = None


    # ==========================
    # APPLICATION
    # ==========================

    BASE_URL: str = "http://127.0.0.1:8000"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()