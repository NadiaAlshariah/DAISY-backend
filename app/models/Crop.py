from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.enum.CropTypeEnum import CropType
from app.enum.GrowthStateEnum import GrowthState

class Crop(BaseModel):
    id: Optional[str] = None
    crop_type: CropType  
    growth_state: GrowthState
    planted_at: datetime = datetime.now()
