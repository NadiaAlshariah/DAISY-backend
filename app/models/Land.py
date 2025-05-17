from app.enum.RainfallPatternEnum import RainfallPatternEnum
from pydantic import BaseModel
from typing import Optional


class Land(BaseModel):
    id: Optional[str] = None
    current_humidity: float
    current_temperature: float
    wind_speed: float
    evapotranspiration: float
    rainfall_pattern : RainfallPatternEnum
    user_id: str
    #list of blocks?

