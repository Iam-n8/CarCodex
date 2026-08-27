# maintenance_visit.py 
# Schema for MaintenanceVisit

from pydantic import BaseModel


class MaintenanceVisitCreate(BaseModel):

    vehicle_id: int

    vendor_id: int | None = None

    visit_date: str

    mileage: int

    vendor: str

    invoice_number: str

    total_cost: float

    notes: str