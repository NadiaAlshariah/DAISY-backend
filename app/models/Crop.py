from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enum.CropTypeEnum import CropType
from app.enum.GrowthStateEnum import GrowthState

class Crop(BaseModel):
    id: Optional[str] = None
    crop_type: CropType  
    growth_state: GrowthState
    block_id: str
    planted_at: datetime = datetime.now()
