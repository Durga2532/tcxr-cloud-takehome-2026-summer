from pydantic import BaseModel

# Pydantic python library is used to define data models with type validation and default values.

class Address(BaseModel):
    street: str = "Unknown"
    city: str = "Unknown"
    state: str = "Unknown"
    zip_code: int = 0

    class Config:
        extra = "ignore"