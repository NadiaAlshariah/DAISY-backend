from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class IrrigationPrediciton(BaseModel):
    id: Optional[str] = None
    block_id: str
    land_id: str
    user_id: str
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    region: Optional[str] = None
    tempreture: Optional[str] = None
    weather_condition: Optional[str] = None
    water_requirement: Optional[float] = None
    created_at: Optional[datetime] = None