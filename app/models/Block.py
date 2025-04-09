from pydantic import BaseModel
from app.enum.SoilTypeEnum import SoilType

class Block(BaseModel):
    id: str 
    location: str
    land_id: str
    current_soil_moisture: float
    soil_type: SoilType
