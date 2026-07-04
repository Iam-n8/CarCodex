from pydantic import BaseModel


class MileageCreate(BaseModel):
    vehicle_id: int
    mileage: int
    entry_date: str
