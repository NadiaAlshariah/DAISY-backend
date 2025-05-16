from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)