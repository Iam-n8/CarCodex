# --------------------------------------------------
# main.py
#
# Maintain Hub
# Application Entry Point
# --------------------------------------------------


# ==================================================
# Framework
# ==================================================

from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    FileResponse
)

from pathlib import Path

from shared.template_loader import templates


# ==================================================
# Database
# ==================================================

from database import (
    engine,
    SessionLocal
)

from models import (
    Base,
    Vehicle,
    Vendor,
    MaintenanceVisit,
    MaintenanceSchedule,
    ServiceRecord,
    Document
)


# ==================================================
# Application-Wide Routers
# ==================================================

from routers import (
    events,
    costs,
    snapshots,
    factory_reset_ui,
    service_catalog_ui
)


# ==================================================
# Helpers
# ==================================================

from helpers.db_migrations import (
    run_database_migrations
)

from helpers.storage import (
    create_vehicle_folders,
    get_document_folder,
    create_vehicle_info_file
)


# ==================================================
# Vehicle Domain
# ==================================================

from vehicle.routers import (
    vehicles,
    vehicle_ui,
    maintenance,
    maintenance_ui,
    maintenance_visit,
    maintsch_ui,
    maintenance_schedule,
    uploads,
    vendor,
    vendor_ui,
    mileage,
    services,
    vehicle_adv,
    document_vehicle,
)

from house.routers import house_ui


# ==================================================
# Application Setup
# ==================================================

app = FastAPI()

from jinja2 import (
    Environment,
    FileSystemLoader
)

template_loader = FileSystemLoader([
    "templates",
    "vehicle/templates"
])

from shared.template_loader import templates

# ==================================================
# Vehicle Domain Routers
# ==================================================

app.include_router(vehicles.router)
app.include_router(vehicle_ui.router)
app.include_router(vehicle_adv.router)

app.include_router(
    document_vehicle.router
)

app.include_router(maintenance.router)
app.include_router(maintenance_ui.router)
app.include_router(maintenance_visit.router)
app.include_router(maintsch_ui.router)
app.include_router(maintenance_schedule.router)

app.include_router(uploads.router)

app.include_router(vendor.router)
app.include_router(vendor_ui.router)

app.include_router(mileage.router)

app.include_router(services.router)

app.include_router(house_ui.router)

# ==================================================
# Application-Wide Routers
# ==================================================

app.include_router(events.router)
app.include_router(costs.router)
app.include_router(snapshots.router)

app.include_router(service_catalog_ui.router)

app.include_router(factory_reset_ui.router)

# ==================================================
# Database Initialization
# ==================================================

run_database_migrations()

# --------------------------------------------------
# dashboard
# --------------------------------------------------

@app.get(
    "/ui",
    response_class=HTMLResponse
)
def dashboard(
    request: Request
):

    db = SessionLocal()

    vehicle_count = db.query(Vehicle).count()

    vendor_count = db.query(Vendor).count()

    visit_count = db.query(MaintenanceVisit).count()

    document_count = db.query(Document).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "vehicle_count": vehicle_count,
            "vendor_count": vendor_count,
            "visit_count": visit_count,
            "document_count": document_count
        }
    )

@app.get(
    "/icon-test",
    response_class=HTMLResponse
)
def icon_dashboard_test(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="icon_dashboard_test.html",
        context={
            "request": request
        }
    )

@app.get(
    "/svg-test",
    response_class=HTMLResponse
)
def svg_dashboard_test(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="svg_dashboard_test.html",
        context={
            "request": request
        }
    )

@app.get(
    "/svg-six-test",
    response_class=HTMLResponse
)
def svg_dashboard_six_test(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="svg_dashboard_six_test.html",
        context={
            "request": request
        }
    )

@app.get(
    "/svg-sheet-test",
    response_class=HTMLResponse
)
def svg_sheet_test(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="svg_sheet_test.html",
        context={
            "request": request
        }
    )

@app.get("/svg/{filename}")
def serve_svg(filename: str):
    svg_dir = Path(__file__).resolve().parent / "vehicle" / "templates" / "SVG"
    possible_paths = [
        svg_dir / filename,
        svg_dir / f"{filename}.svg",
        svg_dir / f"{filename}.svg.xml",
        svg_dir / f"{filename}.xml",
    ]

    for candidate in possible_paths:
        if candidate.exists() and candidate.is_file():
            return FileResponse(
                path=str(candidate),
                media_type="image/svg+xml",
                filename=candidate.name
            )

    raise HTTPException(status_code=404, detail="SVG not found")


@app.get("/service-icon/{filename}")
def serve_service_icon(filename: str):
    icon_dir = Path(__file__).resolve().parent / "vehicle" / "templates" / "images" / "png"
    possible_paths = [
        icon_dir / filename,
        icon_dir / f"{filename}.png",
        icon_dir / f"{filename}.PNG",
    ]

    for candidate in possible_paths:
        if candidate.exists() and candidate.is_file():
            return FileResponse(
                path=str(candidate),
                media_type="image/png",
                filename=candidate.name
            )

    raise HTTPException(status_code=404, detail="Service icon not found")

@app.get(
    "/maintenance-visit/{visit_id}",
    response_class=HTMLResponse
)
def maintenance_visit_detail(
    request: Request,
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

        return RedirectResponse(
            url="/vehicles-ui",
            status_code=303
        )

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == visit.vehicle_id
    ).first()

    vendor = None

    if visit.vendor_id is not None:

        vendor = db.query(
            Vendor
        ).filter(
            Vendor.id == visit.vendor_id
        ).first()

    services = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.maintenance_visit_id == visit_id,
        ServiceRecord.archived == False
    ).all()

    documents = db.query(
        Document
    ).filter(
        Document.maintenance_visit_id == visit_id,
        Document.domain == "Vehicle",
        Document.archived == False
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_visit_detail.html",
        context={
            "request": request,
            "visit": visit,
            "vehicle": vehicle,
            "vendor": vendor,
            "services": services,
            "documents": documents
        }
    )
# --------------------------------------------------
# Settings
# --------------------------------------------------

@app.get(
    "/settings",
    response_class=HTMLResponse
)
def settings_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "request": request
        }
    )

@app.get(
    "/legal",
    response_class=HTMLResponse
)
def legal_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="legal.html",
        context={
            "request": request
        }
    )
