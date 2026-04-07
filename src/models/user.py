from pydantic import BaseModel, Field
from typing import Optional
from .address import Address

class User(BaseModel):
    user_id: Optional[int] = None
    first_name: str = "Unknown"
    last_name: str = "Unknown"
    email: str = "unknown@xyz.com"
    role: str = "User"
    address: Address = Field(default_factory=Address)
    phone: str = "Unknown"
    is_active: bool = False
    last_login: str = "1970-01-01T00:00:00Z"

    class Config:
        extra = "ignore"