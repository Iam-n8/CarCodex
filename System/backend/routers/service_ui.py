# --------------------------------------------------
# service_ui.py
#
# Service Record User Interface Routes
#
# Purpose:
#
# - Add Service Records
# - Edit Service Records
# - Archive Service Records
#
# NOTE:
#
# Service Records are now automatically
# created during Maintenance Visit creation.
#
# These routes are still needed for:
#
# - Editing Service Records
# - Archiving Service Records
#
# Future consideration:
#
# Remove manual Service Record creation
# if it is no longer required.
#
# --------------------------------------------------

from fastapi import (
    APIRouter,
    Request,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from database import (
    SessionLocal
)

from models import (
    ServiceRecord,
    ServiceType,
    MaintenanceVisit
)

# --------------------------------------------------
# Router
# --------------------------------------------------

router = APIRouter()

# --------------------------------------------------
# Templates
# --------------------------------------------------

templates = Jinja2Templates(
    directory="templates"
)

# --------------------------------------------------
# Add Service Record Page
# --------------------------------------------------

@router.get(
    "/service-add/{visit_id}",
    response_class=HTMLResponse
)
def service_add_page(
    request: Request,
    visit_id: int
):

    db = SessionLocal()

    service_types = db.query(
        ServiceType
    ).filter(
        ServiceType.archived == False
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="service_add.html",
        context={
            "request": request,
            "visit_id": visit_id,
            "service_types": service_types
        }
    )


# --------------------------------------------------
# Add Service Record Submit
# --------------------------------------------------

@router.post(
    "/service-add/{visit_id}"
)
def service_add_submit(

    visit_id: int,

    primary_reason: str = Form(...),

    other_service: str = Form(""),

    parts_used: str = Form(""),

    additional_services: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    if primary_reason == "Other":

        primary_reason = other_service

        existing = db.query(
            ServiceType
        ).filter(
            ServiceType.name == primary_reason
        ).first()

        if not existing:

            db.add(
                ServiceType(
                    name=primary_reason
                )
            )

            db.commit()

    service = ServiceRecord(

        vehicle_id=visit.vehicle_id,

        maintenance_visit_id=visit_id,

        primary_reason=primary_reason,

        parts_used=parts_used,

        additional_services=additional_services,

        notes=notes,

        service_status="COMPLETED"
    )

    db.add(service)

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintenance-visit/{visit_id}",
        status_code=303
    )


# --------------------------------------------------
# Edit Service Record Page
# --------------------------------------------------

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

    return templates.TemplateResponse(
        request=request,
        name="service_edit.html",
        context={
            "request": request,
            "service": service
        }
    )


# --------------------------------------------------
# Edit Service Record Submit
# --------------------------------------------------

@router.post(
    "/service-edit/{service_id}"
)
def service_edit_submit(

    service_id: int,

    primary_reason: str = Form(...),

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

    service.primary_reason = primary_reason
    service.parts_used = parts_used
    service.additional_services = additional_services
    service.notes = notes

    visit_id = service.maintenance_visit_id

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintenance-visit/{visit_id}",
        status_code=303
    )


# --------------------------------------------------
# Archive Service Record Page
# --------------------------------------------------

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

    return templates.TemplateResponse(
        request=request,
        name="service_archive.html",
        context={
            "request": request,
            "service": service
        }
    )


# --------------------------------------------------
# Archive Service Record Submit
# --------------------------------------------------

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

    visit_id = service.maintenance_visit_id

    service.archived = True

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintenance-visit/{visit_id}",
        status_code=303
    )