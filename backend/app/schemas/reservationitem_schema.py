from pydantic import BaseModel, ConfigDict




class ReservationItemResponse(BaseModel):

    id: int
    reservation_id: int
    service_id: int

    model_config = ConfigDict(from_attributes=True)
