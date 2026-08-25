from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReservationCreate(BaseModel):

    name: str
    phone: str
    email: str | None = None
    service_ids: list[int]
    start_at: datetime




class ReservationResponse(BaseModel):

    id: int
    client_id: int
    start_at: datetime
    end_at: datetime
    status: str
    deposit_amount: int
    phone_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes= True)
