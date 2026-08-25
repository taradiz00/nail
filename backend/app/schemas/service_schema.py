from pydantic import BaseModel, ConfigDict

class ServiceCreate(BaseModel):
    name: str
    category: str
    price: int | None = None
    deposit_amount: int
    duration_minutes: int
    is_active: bool = True


class ServiceResponse(BaseModel):
    id: int
    name: str
    category: str
    price: int | None = None
    deposit_amount: int
    duration_minutes: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes= True)