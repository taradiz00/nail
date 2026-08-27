from pydantic import BaseModel, Field

class VerificationRequest(BaseModel):
    reservation_id: int
    code: int


class VerificationConfirm(BaseModel):
    reservation_id: int
    code: str = Field(
        min_length=6,
        max_length=6,)