from pydantic import BaseModel
from typing import Optional, List

class Land(BaseModel):
    id: Optional[str] = None
    user_id: str
    latitude : float
    longitude : float
    sensors: Optional[List[str]] = []
    wifi_ssid : Optional[str] = None
    name: str


