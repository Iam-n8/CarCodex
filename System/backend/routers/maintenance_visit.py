# maintenance_visit.py
from fastapi import APIRouter

from database import SessionLocal
from models import MaintenanceVisit

from schemas.maintenance_visit import (
    MaintenanceVisitCreate
)

router = APIRouter()


@router.get("/maintenance-visits")
def get_maintenance_visits():

    db = SessionLocal()

    visits = db.query(
        MaintenanceVisit
    ).all()

    results = []

    for visit in visits:

        results.append({
            "id": visit.id,
            "vehicle_id": visit.vehicle_id,
            "visit_date": visit.visit_date,
            "mileage": visit.mileage,
            "vendor": visit.vendor,
            "invoice_number": visit.invoice_number,
            "total_cost": visit.total_cost
        })

    db.close()

    return results


@router.post("/maintenance-visits")
def create_maintenance_visit(
    visit: MaintenanceVisitCreate
):

    db = SessionLocal()

    new_visit = MaintenanceVisit(
        vehicle_id=visit.vehicle_id,
        visit_date=visit.visit_date,
        mileage=visit.mileage,
        vendor=visit.vendor,
        invoice_number=visit.invoice_number,
        total_cost=visit.total_cost,
        notes=visit.notes
    )

    db.add(new_visit)

    db.commit()

    db.refresh(new_visit)

    db.close()

    return {
        "message": "Maintenance visit added",
        "id": new_visit.id
    }