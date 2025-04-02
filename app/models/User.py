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

    @field_validator("password_hash", mode="before")
    @classmethod
    def hash_password(cls, value: str) -> str:
        """Hash the password before storing it."""
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return generate_password_hash(value)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {"user", "admin", "moderator"}:
            raise ValueError("Invalid role")
        return value

