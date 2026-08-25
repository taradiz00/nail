from pydantic import BaseModel

class VerificationRequest(BaseModel):
    reservation_id: int
    code: int


class VerificationConfirm(BaseModel):
    reservation_id: int
    code: str