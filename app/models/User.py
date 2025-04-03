from pydantic import BaseModel,EmailStr, field_validator
from datetime import datetime
from werkzeug.security import generate_password_hash
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    password_hash: str
    role: str = "user"
    created_at: datetime = datetime.now()

    def __init__(self, username: str, email: str, password: str, role: str = "user", **kwargs):
        super().__init__(
            username=username,
            email=email,
            password_hash=password,
            role=role,
            **kwargs
        )


    @field_validator("role")
    @staticmethod
    def validate_role(cls, value: str) -> str:
        if value not in {"user", "admin", "moderator"}:
            raise ValueError("Invalid role")
        return value

