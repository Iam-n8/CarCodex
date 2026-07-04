from pydantic import BaseModel


class ServiceCreate(BaseModel):
    vehicle_id: int
    service_type: str
    service_date: str
    mileage: int
    provider: str
    cost: int
    notes: str
    next_service_mileage: int
    next_service_date: str