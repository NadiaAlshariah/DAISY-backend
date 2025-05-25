from pydantic import BaseModel
from datetime import date

class Prediction(BaseModel):
    land_id : str
    block_id : str
    water_requirement : float
    unit : str
    timestamp : date
