# maintenance_schedule.py

from pydantic import BaseModel


class MaintenanceScheduleCreate(BaseModel):
    vehicle_id: int

    service_type: str

    interval_miles: int

    interval_months: int

    estimated_cost: float

    uses_health_indicator: str

    notes: str