from fastapi import FastAPI
from pydantic import BaseModel

from database import engine, SessionLocal

from models import (
    Base,
    Vehicle,
    ServiceRecord,
    MileageHistory
)


app = FastAPI()

Base.metadata.create_all(bind=engine)


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


@app.post("/mileage")
def add_mileage(mileage: MileageCreate):

    db = SessionLocal()

    new_entry = MileageHistory(
        vehicle_id=mileage.vehicle_id,
        mileage=mileage.mileage,
        entry_date=mileage.entry_date
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    db.close()

    return {
        "message": "Mileage added",
        "id": new_entry.id
    }


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


@app.get("/")
def root():
    return {
        "app": "CarCodex",
        "version": "1.0.1",
        "status": "running"
    }


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

    db.close()

    return {
        "message": "Vehicle added",
        "id": new_vehicle.id
    }


@app.get("/vehicles")
def get_vehicles():

    db = SessionLocal()

    vehicles = db.query(Vehicle).all()

    results = []

    for vehicle in vehicles:
        results.append(
            {
                "id": vehicle.id,
                "nickname": vehicle.nickname,
                "year": vehicle.year,
                "make": vehicle.make,
                "model": vehicle.model,
                "mileage": vehicle.current_mileage
            }
        )

    db.close()

    return results


@app.post("/services")
def create_service(service: ServiceCreate):

    db = SessionLocal()

    new_service = ServiceRecord(
        vehicle_id=service.vehicle_id,
        service_type=service.service_type,
        service_date=service.service_date,
        mileage=service.mileage,
        provider=service.provider,
        cost=service.cost,
        notes=service.notes,
        next_service_mileage=service.next_service_mileage,
        next_service_date=service.next_service_date
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    db.close()

    return {
        "message": "Service added",
        "id": new_service.id
    }


@app.get("/services")
def get_services():

    db = SessionLocal()

    services = db.query(ServiceRecord).all()

    results = []

    for service in services:
        results.append(
            {
                "id": service.id,
                "vehicle_id": service.vehicle_id,
                "service_type": service.service_type,
                "date": service.service_date,
                "mileage": service.mileage,
                "cost": service.cost
            }
        )

    db.close()

    return results