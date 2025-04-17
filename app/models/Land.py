from pydantic import BaseModel
from typing import Optional


class Land(BaseModel):
    id: Optional[str] = None
    current_humidity: float
    current_temperature: float
    user_id: str

