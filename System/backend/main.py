import os
from routers import vehicles

from fastapi import FastAPI

from pydantic import BaseModel

from database import engine, SessionLocal

from routers import mileage
from routers import events
from routers import documents
from routers import costs
from routers import snapshots


from models import (
    Base,
    Vehicle,
    ServiceRecord,
    MileageHistory,
    Event,
    Snapshot,
    OwnershipCost,
    Document
)
# --------------------------------------------------
# Routers
# --------------------------------------------------
from routers import services
app = FastAPI()
app.include_router(vehicles.router)
app.include_router(services.router) 
app.include_router(mileage.router)
app.include_router(events.router)
app.include_router(documents.router)
app.include_router(costs.router)
app.include_router(snapshots.router)


Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def create_vehicle_folders(vehicle_id):

    base_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Documents",
            f"VEH_{vehicle_id:06d}"
        )
    )

    folders = [
        "Maintenance",
        "Repairs",
        "Mods",
        "Insurance",
        "Registration",
        "Tires",
        "Events",
        "Photos",
        "Warranty",
        "Reports",
        "Misc"
    ]

    os.makedirs(base_folder, exist_ok=True)

    for folder in folders:
        os.makedirs(
            os.path.join(base_folder, folder),
            exist_ok=True
        )


# --------------------------------------------------
# Schemas
# --------------------------------------------------

class VehicleCreate(BaseModel):
    nickname: str
    vin: str
    year: int
    make: str
    model: str
    trim: str
    current_mileage: int


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


class MileageCreate(BaseModel):
    vehicle_id: int
    mileage: int
    entry_date: str


class EventCreate(BaseModel):
    vehicle_id: int
    event_date: str
    mileage: int
    category: str
    event_type: str
    description: str
    cost: int


class SnapshotCreate(BaseModel):
    timestamp: str
    action: str
    description: str
    vehicle_id: int


class OwnershipCostCreate(BaseModel):
    vehicle_id: int
    cost_date: str
    category: str
    description: str
    vendor: str
    amount: float
    mileage: int


class DocumentCreate(BaseModel):
    vehicle_id: int
    document_type: str
    file_name: str
    file_path: str
    upload_date: str
    notes: str


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "app": "CarCodex",
        "version": "1.0.1",
        "status": "running"
    }


# --------------------------------------------------
# Vehicles
# --------------------------------------------------


# --------------------------------------------------
# Services
# --------------------------------------------------

# --------------------------------------------------
# Mileage
# --------------------------------------------------

# --------------------------------------------------
# Events
# --------------------------------------------------

# --------------------------------------------------
# Documents
# --------------------------------------------------
