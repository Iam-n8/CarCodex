from pydantic import BaseModel


class VehicleCreate(BaseModel):
    nickname: str
    vin: str
    year: int
    make: str
    model: str
    trim: str
    current_mileage: int