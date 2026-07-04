from fastapi import APIRouter
from schemas.vehicle import VehicleCreate

from database import SessionLocal
from models import Vehicle

router = APIRouter()


@router.get("/vehicles")
def get_vehicles():

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
@router.post("/vehicles")
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