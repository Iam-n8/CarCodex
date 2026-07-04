from fastapi import APIRouter
from pydantic import BaseModel

from database import SessionLocal
from models import Vehicle

router = APIRouter()


class VehicleCreate(BaseModel):
    nickname: str
    vin: str
    year: int
    make: str
    model: str
    trim: str
    current_mileage: int


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