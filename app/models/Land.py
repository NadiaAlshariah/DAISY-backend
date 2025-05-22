from pydantic import BaseModel
from typing import Optional

class Land(BaseModel):
    id: Optional[str] = None
    user_id: str
    latitude : float
    longitude : float
    name: str

