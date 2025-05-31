from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone


class YieldPrediction(BaseModel):
    id: Optional[str] = None
    block_id: str
    land_id: str
    user_id: str
    region: Optional[str] = None
    soil_type: Optional[str] = None
    crop: Optional[str] = None
    rainfall_mm: Optional[float] = None
    temperature_celsius: Optional[float] = None
    fertilizer_used: Optional[bool] = None
    irrigation_used: Optional[bool] = None
    weather_condition: Optional[str] = None
    days_to_harvest: Optional[int] = None
    yield_tons_per_hectare: Optional[float] = None
    created_at: Optional[datetime] = None