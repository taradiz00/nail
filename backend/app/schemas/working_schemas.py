from pydantic import BaseModel, ConfigDict
from datetime import time

class WorkingHoursCreate(BaseModel):
    weekday: int
    start_time: time 
    end_time: time


class WorkingHoursResponse(BaseModel):
    id: int
    weekday: int
    start_time: time 
    end_time: time

    model_config = ConfigDict(from_attributes= True)