from pydantic import BaseModel, ConfigDict


class PaymentRequest(BaseModel):
    reservation_id: int


class PaymentResponse(BaseModel):
    reservation_id: int
    amount: int
    message: str

    model_config = ConfigDict(from_attributes= True)