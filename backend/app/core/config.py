from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "test"
    SQLALCHEMY_DATABASE_URL: str
    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    BASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()