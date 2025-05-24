from pydantic import BaseModel
from app.enum.CropTypeEnum import CropType
from app.enum.GrowthStateEnum import GrowthState

class CropModel(BaseModel):
    crop_type: CropType
    growth_state: GrowthState
    crop_water_requirement: float

    def to_dict(self):
        return {
            "crop_type": self.crop_type.value,
            "growth_state": self.growth_state.value,
            "crop_water_requirement": self.crop_water_requirement
        }