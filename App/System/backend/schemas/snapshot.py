from pydantic import BaseModel


class SnapshotCreate(BaseModel):
    timestamp: str
    action: str
    description: str
    vehicle_id: int