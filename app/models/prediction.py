from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Prediction(BaseModel):
    id: Optional[str] = None
    land_id: str
    block_id: str
    water_requirement: float
    unit: str = "mm/day"
    timestamp: Optional[datetime] = None