from pydantic import BaseModel
from app.enum.SoilTypeEnum import SoilType
from typing import Optional


class Block(BaseModel):
    id: Optional[str] = None
    location: str
    land_id: str
    current_soil_moisture: float
    soil_type: SoilType
