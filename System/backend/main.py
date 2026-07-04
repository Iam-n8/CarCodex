import os
from routers import vehicles

from fastapi import FastAPI

from pydantic import BaseModel

from database import engine, SessionLocal

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

app = FastAPI()
app.include_router(vehicles.router)

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

@app.post("/vehicles")
def create_vehicle(vehicle: VehicleCreate):

    db = SessionLocal()

    new_vehicle = Vehicle(
        nickname=vehicle.nickname,
        vin=vehicle.vin,
        year=vehicle.year,
        make=vehicle.make,
        model=vehicle.model,
        trim=vehicle.trim,
        current_mileage=vehicle.current_mileage
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    create_vehicle_folders(new_vehicle.id)

    db.close()

    return {
        "message": "Vehicle added",
        "id": new_vehicle.id
    }



    db = SessionLocal()

    vehicles = db.query(Vehicle).all()

    results = []

    for vehicle in vehicles:
        results.append({
            "id": vehicle.id,
            "nickname": vehicle.nickname,
            "year": vehicle.year,
            "make": vehicle.make,
            "model": vehicle.model,
            "mileage": vehicle.current_mileage
        })

    db.close()

    return results


# --------------------------------------------------
# Services
# --------------------------------------------------

@app.get("/services")
def get_services():

    db = SessionLocal()

    services = db.query(ServiceRecord).all()

    results = []

    for service in services:
        results.append({
            "id": service.id,
            "vehicle_id": service.vehicle_id,
            "service_type": service.service_type
        })

    db.close()

    return results


# --------------------------------------------------
# Mileage
# --------------------------------------------------

@app.get("/mileage")
def get_mileage():

    db = SessionLocal()

    records = db.query(MileageHistory).all()

    results = []

    for record in records:
        results.append({
            "vehicle_id": record.vehicle_id,
            "mileage": record.mileage,
            "entry_date": record.entry_date
        })

    db.close()

    return results


# --------------------------------------------------
# Events
# --------------------------------------------------

@app.get("/events")
def get_events():

    db = SessionLocal()

    events = db.query(Event).all()

    results = []

    for event in events:
        results.append({
            "id": event.id,
            "event_type": event.event_type
        })

    db.close()

    return results


# --------------------------------------------------
# Documents
# --------------------------------------------------

@app.get("/documents")
def get_documents():

    db = SessionLocal()

    docs = db.query(Document).all()

    results = []

    for doc in docs:
        results.append({
            "id": doc.id,
            "file_name": doc.file_name
        })

    db.close()

    return results