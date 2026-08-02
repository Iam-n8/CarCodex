# service_ui.py

from fastapi import (
    APIRouter,  
    Request,
    Form
)   


# --------------------------------------------------
# Add Service Record Page
# --------------------------------------------------

@app.get(
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
@app.post(
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

@app.get(
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
@app.post(
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

@app.get(
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
@app.post(
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