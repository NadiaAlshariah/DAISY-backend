from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Land(BaseModel):
    id: Optional[str] = None
    current_humidity: float
    current_temperature: float

