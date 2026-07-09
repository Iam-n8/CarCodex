# maintenance_visit.py

from fastapi import APIRouter

from database import SessionLocal

from models import (
    MaintenanceVisit,
    ServiceRecord,
    Document,
    Vendor
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

        vendor_id=visit.vendor_id,

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

    vendor_name = None

    if visit.vendor_id:

        vendor = db.query(Vendor).filter(
            Vendor.id == visit.vendor_id
        ).first()

        if vendor:
            vendor_name = vendor.name

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

    document_list = []

    for document in documents:

        document_list.append({
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type
        })

    result = {
        "visit_id": visit.id,
        "vehicle_id": visit.vehicle_id,

        "vendor_id": visit.vendor_id,
        "vendor_name": vendor_name,

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

@router.put("/maintenance-visits/{visit_id}")
def update_maintenance_visit(
    visit_id: int,
    visit_data: MaintenanceVisitCreate
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

    visit.vehicle_id = visit_data.vehicle_id

    visit.vendor_id = visit_data.vendor_id

    visit.visit_date = visit_data.visit_date

    visit.mileage = visit_data.mileage

    visit.vendor = visit_data.vendor

    visit.invoice_number = visit_data.invoice_number

    visit.total_cost = visit_data.total_cost

    visit.notes = visit_data.notes

    db.commit()

    db.close()

    return {
        "message": "Maintenance visit updated"
    }