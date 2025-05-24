from app.enum.SensorStatusEnum import SensorStatus
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Sensor(BaseModel):
    id : Optional[str] = None
    mac_address : str
    pin : int
    block_id : Optional[str] = None
    land_id : str
    status : SensorStatus
    last_heartbeat: datetime