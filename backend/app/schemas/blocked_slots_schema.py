from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BlockedSlotsCreate(BaseModel):
    start_at: datetime
    end_at: datetime
    reason: str | None = None



class BlockedSlotsResponse(BaseModel):
    id: int
    start_at: datetime
    end_at: datetime
    reason: str | None = None

    model_config = ConfigDict(from_attributes= True)