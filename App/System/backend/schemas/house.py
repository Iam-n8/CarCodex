from pydantic import BaseModel, Field


class HouseAddressLookup(BaseModel):
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=3, max_length=10)
    country: str = "US"
