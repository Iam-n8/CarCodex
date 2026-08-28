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
    Form
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)


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
    Document,
    ServiceRecord
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
    maintsch_ui
)

from routers.vehicle import (
    vehicle_adv
)


# ==================================================
# Application Setup
# ==================================================

app = FastAPI()

templates = Jinja2Templates(
    directory="templates"
)
# ==================================================
# Vehicle Domain Routers
# ==================================================

app.include_router(vehicles.router)
app.include_router(vehicle_ui.router)
app.include_router(vehicle_adv.router)

app.include_router(maintenance.router)
app.include_router(maintenance_ui.router)
app.include_router(maintenance_visit.router)
app.include_router(maintsch_ui.router)
app.include_router(maintenance_schedule.router)
app.include_router(maintsch_ui.router)

app.include_router(uploads.router)

app.include_router(vendor.router)
app.include_router(vendor_ui.router)

app.include_router(mileage.router)

app.include_router(services.router)

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
