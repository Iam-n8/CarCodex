from pydantic import BaseModel


class EventCreate(BaseModel):
    vehicle_id: int
    event_date: str
    mileage: int
    category: str
    event_type: str
    description: str
    location: str
    # cost: int
    cost: float

    