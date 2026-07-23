# main.py

# import os
from routers import vehicles
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


# --------------------------------------------------
# Routers
# --------------------------------------------------
from routers import services
app = FastAPI()

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
@app.get(
    "/vehicles-ui",
    response_class=HTMLResponse
)
def vehicles_ui(
    request: Request
):

    db = SessionLocal()

    vehicles = db.query(Vehicle).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicles.html",
        context={
            "request": request,
            "vehicles": vehicles
        }
    )
@app.get(
    "/vehicle/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_detail(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    visits = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.vehicle_id == vehicle_id
    ).all()

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_detail.html",

        context={
            "request": request,
            "vehicle": vehicle,
            "visits": visits,

            "schedules": schedules,

            "visit_count": len(visits),

            "document_count": 0,

            "vendor_count": 0
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
        ServiceRecord.maintenance_visit_id == visit_id
    ).all()



    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_visit_detail.html",
        context={
            "request": request,
            "visit": visit,
            "services": services
        }
    )
# --------------------------------------------------
# Add Vehicle Page
# --------------------------------------------------

@app.get(
    "/vehicle-add",
    response_class=HTMLResponse
)
def vehicle_add_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="vehicle_add.html",
        context={
            "request": request
        }
    )


# --------------------------------------------------
# Add Vehicle Submit
# --------------------------------------------------

@app.post(
    "/vehicle-add"
)
def vehicle_add_submit(

    nickname: str = Form(...),

    year: int = Form(...),

    make: str = Form(...),

    model: str = Form(...),

    trim: str = Form(...),

    vin: str = Form(...),

    current_mileage: int = Form(...)

):

    db = SessionLocal()

    vehicle = Vehicle(

        nickname=nickname,

        year=year,

        make=make,

        model=model,

        trim=trim,

        vin=vin,

        current_mileage=current_mileage

    )

    db.add(vehicle)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )