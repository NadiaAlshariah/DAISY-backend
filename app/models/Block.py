from app.enum.DrainagePropertiesEnum import DrainagePropertiesEnum
from pydantic import BaseModel
from app.enum.SoilTypeEnum import SoilType
from typing import Optional
from datetime import datetime
from app.enum.CropTypeEnum import CropType
from app.enum.GrowthStateEnum import GrowthState


class Block(BaseModel):
    id: Optional[str] = None
    land_id: str
    current_soil_moisture: float
    soil_type: SoilType
    water_retention_capacity: float  
    drainage_properties: DrainagePropertiesEnum
    crop_type: CropType  
    growth_state: GrowthState
    block_id: str
    planted_at: datetime = datetime.now()
    crop_water_requirement: float
    sensor_id : Optional[str] = None