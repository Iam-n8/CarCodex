# maintenance_visit.py 
# Schema for MaintenanceVisit

from pydantic import BaseModel


class MaintenanceVisitCreate(BaseModel):

    vehicle_id: int

    visit_date: str

    mileage: int

    vendor: str

    invoice_number: str

    total_cost: float

    notes: str