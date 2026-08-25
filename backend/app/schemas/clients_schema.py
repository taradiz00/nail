from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.utils import normalize_phone

class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(max_length=20)
    email: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, phone: str):
        return normalize_phone(phone)


class ClientResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None

    model_config = ConfigDict(from_attributes= True)