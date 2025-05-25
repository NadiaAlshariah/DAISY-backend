from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enum.CropTypeEnum import CropType
from app.enum.GrowthStateEnum import GrowthState


class Block(BaseModel):
    id: Optional[str] = None
    land_id: str
    crop_type: CropType
    growth_state: GrowthState
    planted_at: datetime = datetime.now()

    sensor_id : Optional[str] = None
    soil_moisture: Optional[float] = None
    region = Optional[str] = None

    crop_water_requirement: Optional[float] = None