from pydantic import BaseModel


class OwnershipCostCreate(BaseModel):
    vehicle_id: int
    cost_date: str
    category: str
    description: str
    vendor: str
    amount: float
    mileage: int