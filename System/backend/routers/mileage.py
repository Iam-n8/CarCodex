from fastapi import APIRouter
from pydantic import BaseModel

from database import SessionLocal
from models import MileageHistory

router = APIRouter()


class MileageCreate(BaseModel):
    vehicle_id: int
    mileage: int
    entry_date: str


@router.get("/mileage")
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


@router.post("/mileage")
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