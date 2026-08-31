# service.py
# Routers

from fastapi import (
    APIRouter,
    Request,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from shared.template_loader import (
    templates
)

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

@router.get(
    "/services-archived",
    response_class=HTMLResponse
)
def archived_services_page(
    request: Request
):

    db = SessionLocal()

    services = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.archived == True
    ).order_by(
        ServiceRecord.id.desc()
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="archived_services.html",
        context={
            "request": request,
            "services": services
        }
    )


@router.post(
    "/service-restore/{service_id}"
)
def restore_service_record(
    service_id: int
):

    db = SessionLocal()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.id == service_id
    ).first()

    if service:
        service.archived = False
        db.commit()

    db.close()

    return RedirectResponse(
        url="/services-archived",
        status_code=303
    )

@router.get(
    "/service-edit/{service_id}",
    response_class=HTMLResponse
)
def service_edit_page(
    request: Request,
    service_id: int
):

    db = SessionLocal()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.id == service_id
    ).first()

    db.close()

    if not service:
        return RedirectResponse(
            url="/maintenance-ui",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="service_edit.html",
        context={
            "request": request,
            "service": service
        }
    )


@router.post(
    "/service-edit/{service_id}"
)
def service_edit_submit(
    service_id: int,
    primary_reason: str = Form(""),
    parts_used: str = Form(""),
    additional_services: str = Form(""),
    notes: str = Form("")
):

    db = SessionLocal()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.id == service_id
    ).first()

    if not service:
        db.close()
        return RedirectResponse(
            url="/maintenance-ui",
            status_code=303
        )

    service.primary_reason = primary_reason.strip() or None
    service.parts_used = parts_used.strip() or None
    service.additional_services = additional_services.strip() or None
    service.notes = notes.strip() or None

    db.commit()
    db.close()

    if service.maintenance_visit_id:
        return RedirectResponse(
            url=f"/maintenance-visit/{service.maintenance_visit_id}",
            status_code=303
        )

    return RedirectResponse(
        url="/maintenance-ui",
        status_code=303
    )


@router.get(
    "/service-archive/{service_id}",
    response_class=HTMLResponse
)
def service_archive_page(
    request: Request,
    service_id: int
):

    db = SessionLocal()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.id == service_id
    ).first()

    db.close()

    if not service:
        return RedirectResponse(
            url="/maintenance-ui",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="service_archive.html",
        context={
            "request": request,
            "service": service
        }
    )


@router.post(
    "/service-archive/{service_id}"
)
def service_archive_submit(
    service_id: int
):

    db = SessionLocal()

    service = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.id == service_id
    ).first()

    if not service:
        db.close()
        return RedirectResponse(
            url="/maintenance-ui",
            status_code=303
        )

    visit_id = service.maintenance_visit_id
    service.archived = True

    db.commit()
    db.close()

    if visit_id:
        return RedirectResponse(
            url=f"/maintenance-visit/{visit_id}",
            status_code=303
        )

    return RedirectResponse(
        url="/maintenance-ui",
        status_code=303
    )