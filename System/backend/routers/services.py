# service.py
# Routers   

from fastapi import APIRouter

from schemas.service import ServiceCreate

from database import SessionLocal
from models import ServiceRecord

router = APIRouter()

@router.get("/services")
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


@router.post("/services")
def create_service(service: ServiceCreate):

    db = SessionLocal()

    new_service = ServiceRecord(
        vehicle_id=service.vehicle_id,
        maintenance_visit_id=service.maintenance_visit_id,
        
        service_status=
            service.service_status,

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