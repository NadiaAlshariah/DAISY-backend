from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enum.CropTypeEnum import CropType



class Block(BaseModel):
    id: Optional[str] = None
    land_id: str
    soil_moisture: Optional[float] = None
    crop_type: Optional[CropType] = None

    rainfall_mm: float = 0.0
    fertilizer_uesd: bool = False
    irrigation_used: bool = False
    planted_at: datetime = datetime.now()

    sensor_id: Optional[str] = None


    class Config:
        use_enum_values = True

    
    def add_rainfall(self, amount: float):
        if amount is not None and amount >= 0:
            self.rainfall_mm += amount
    

    def get_soil_type_category(self) -> str:
        if self.soil_moisture is None:
            return "unknown"
        if self.soil_moisture < 15:
            return "DRY"
        elif self.soil_moisture < 35:
            return "HUMID"
        else:
            return "WET"


    def get_soil_texture(self) -> str:
        if self.soil_moisture is None:
            return "unknown"
        if self.soil_moisture < 10:
            return "Sandy"
        elif self.soil_moisture < 20:
            return "Clay"
        elif self.soil_moisture < 30:
            return "Loam"
        elif self.soil_moisture < 40:
            return "Silt"
        elif self.soil_moisture < 50:
            return "Peaty"
        else:
            return "Chalky"
        