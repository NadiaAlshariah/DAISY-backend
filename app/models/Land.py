from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from Block import Block
from typing import List


class Land(BaseModel):
    id: Optional[str] = None
    current_humidity: float
    current_temperature: float
    created_at: datetime = datetime.now()
    blocks: List[Block] = []

