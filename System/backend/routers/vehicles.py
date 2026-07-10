from fastapi import APIRouter
from schemas.vehicle import VehicleCreate
from helpers.filesystem import create_vehicle_folders

from database import SessionLocal
from models import Vehicle

router = APIRouter()


@router.get("/vehicles")
def get_vehicles():

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == False
    ).all()

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

    create_vehicle_folders(new_vehicle.id)

    db.close()

    return {
        "message": "Vehicle added",
        "id": new_vehicle.id
    }
@router.put("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleCreate
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:

        db.close()

        return {
            "error": "Vehicle not found"
        }

    vehicle.nickname = vehicle_data.nickname

    vehicle.vin = vehicle_data.vin

    vehicle.year = vehicle_data.year

    vehicle.make = vehicle_data.make

    vehicle.model = vehicle_data.model

    vehicle.trim = vehicle_data.trim

    vehicle.current_mileage = (
        vehicle_data.current_mileage
    )

    db.commit()

    db.close()

    return {
        "message": "Vehicle updated"
    }
@router.put("/vehicles/{vehicle_id}/archive")
def archive_vehicle(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:

        db.close()

        return {
            "error": "Vehicle not found"
        }

    vehicle.archived = True

    db.commit()

    db.close()

    return {
        "message": "Vehicle archived"
    }
@router.put("/vehicles/{vehicle_id}/restore")
def restore_vehicle(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:

        db.close()

        return {
            "error": "Vehicle not found"
        }

    vehicle.archived = False

    db.commit()

    db.close()

    return {
        "message": "Vehicle restored"
    }
@router.get("/vehicles/archived")
def get_archived_vehicles():

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == True
    ).all()

    results = []

    for vehicle in vehicles:

        results.append({
            "id": vehicle.id,
            "nickname": vehicle.nickname,
            "year": vehicle.year,
            "make": vehicle.make,
            "model": vehicle.model
        })

    db.close()

    return results