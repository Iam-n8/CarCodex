# service.py 
# Schema for ServiceRecord

from pydantic import BaseModel



class ServiceCreate(BaseModel):
    vehicle_id: int

    maintenance_visit_id: int | None = None
    service_status: str = "COMPLETED"

    service_type: str
    service_date: str
    mileage: int
    provider: str
    cost: int
    notes: str
    next_service_mileage: int
    next_service_date: str
