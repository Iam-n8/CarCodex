# main.py

# import os
from routers import maintsch_ui, vehicles
from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)
from fastapi import (
    Request,
    Form
)

from fastapi.templating import Jinja2Templates

from database import engine
from database import SessionLocal

from routers import mileage
from routers import events
from routers import documents
from routers import costs
from routers import snapshots
from models  import Base, ServiceRecord
from routers import uploads
from routers import maintenance
from routers import maintenance_schedule
from routers import maintenance_visit
from routers import vendor
from models import (
    Vehicle,
    Vendor,
    MaintenanceVisit,
    Document,
    MaintenanceSchedule
)

from routers import vehicle_ui
from routers import maintenance_ui
from routers import vendor_ui

from helpers.storage import (
    create_vehicle_folders,
    get_document_folder,
    create_vehicle_info_file
)

from routers import maintsch_ui
from routers import factory_reset_ui

from helpers.db_migrations import (
    run_database_migrations
)


# --------------------------------------------------
# Routers
# --------------------------------------------------
from routers import services
app = FastAPI()

from routers import service_catalog_ui



templates = Jinja2Templates(
    directory="templates"
)

# templates = Jinja2Templates(directory=r"C:\CarCodex\System\backend\templates")

app.include_router(vehicles.router)
app.include_router(services.router) 
app.include_router(mileage.router)
app.include_router(events.router)
app.include_router(documents.router)
app.include_router(costs.router)
app.include_router(snapshots.router)
app.include_router(uploads.router)
app.include_router(maintenance.router)
app.include_router(
    maintenance_schedule.router
)
app.include_router(
    maintenance_visit.router
)
app.include_router(vendor.router)
app.include_router(vehicle_ui.router)
app.include_router(maintenance_ui.router)
app.include_router(
    vendor_ui.router
)

app.include_router(
    maintsch_ui.router
)

app.include_router(
    service_catalog_ui.router
)
app.include_router(
    vehicle_ui.router
)
app.include_router(
    factory_reset_ui.router
)




Base.metadata.create_all(
    bind=engine
)

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