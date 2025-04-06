from pydantic import BaseModel
from typing import List
from models.Crop import Crop
from app.enum.SoilTypeEnum import SoilType

class Block(BaseModel):
    id: str 
    location: str
    crops: List[Crop] = []
    current_soil_moisture: float
    current_temperature: float
    soil_type: SoilType
