from datetime import date
from pydantic import BaseModel, ConfigDict


class AvailabilityRequest(BaseModel):
    date: date
    service_ids: list[int]


class AvailabilityResponse(BaseModel):
    date: date
    total_duration_minutes: int
    available_times: list[str]

    model_config = ConfigDict(from_attributes= True)