# maintenance_visit.py

from fastapi import APIRouter

from database import SessionLocal

from models import (
    MaintenanceVisit,
    ServiceRecord,
    Document
)


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
@router.get("/maintenance-visits/{visit_id}")
def get_maintenance_visit(
    visit_id: int
):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    if not visit:

        db.close()

        return {
            "error": "Maintenance visit not found"
        }

    services = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.maintenance_visit_id == visit_id
    ).all()


    documents = db.query(
        Document
    ).filter(
        Document.maintenance_visit_id == visit_id
    ).all()


    service_list = []

    for service in services:

        service_list.append({
            "service": service.service_type,
            "status": service.service_status
        })

    result = {
        "visit_id": visit.id,
        "vehicle_id": visit.vehicle_id,
        "visit_date": visit.visit_date,
        "mileage": visit.mileage,
        "vendor": visit.vendor,
        "invoice_number": visit.invoice_number,
        "total_cost": visit.total_cost,
        "notes": visit.notes,
        "services": service_list
    }

    document_list = []

    for document in documents:

        document_list.append({
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type
        })

    result["documents"] = document_list
    
    result = {
        "visit_id": visit.id,
        "vehicle_id": visit.vehicle_id,
        "visit_date": visit.visit_date,
        "mileage": visit.mileage,
        "vendor": visit.vendor,
        "invoice_number": visit.invoice_number,
        "total_cost": visit.total_cost,
        "notes": visit.notes,
        "services": service_list,
        "documents": document_list
    }

    db.close()

    return result