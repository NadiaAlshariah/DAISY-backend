from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PredictionModel(BaseModel):
    id: Optional[str] = None
    land_id: str
    block_id: str
    water_requirement: float
    unit: str = "mm/day"
    timestamp: datetime = Field(default_factory=datetime.utcnow)