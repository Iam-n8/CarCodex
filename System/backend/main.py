# main.py

# import os
from routers import vehicles
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from database import engine
from database import SessionLocal

from routers import mileage
from routers import events
from routers import documents
from routers import costs
from routers import snapshots
from models  import Base
from routers import uploads
from routers import maintenance
from routers import maintenance_schedule
from routers import maintenance_visit
from routers import vendor
from models import (
    Vehicle,
    Vendor,
    MaintenanceVisit,
    Document
)


# --------------------------------------------------
# Routers
# --------------------------------------------------
from routers import services
app = FastAPI()

templates = Jinja2Templates(
    directory="templates"
)

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



Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Root
# --------------------------------------------------

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