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
    MaintenanceSchedule,
    ServiceType
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
# Default Service Types
# --------------------------------------------------

db = SessionLocal()

default_service_types = [

    "Oil Change",
    "Brake Service",
    "Tire Service",
    "Transmission Service",
    "Cooling System Service",
    "Inspection",
    "Warranty Repair"

]

for service_name in default_service_types:

    existing = db.query(
        ServiceType
    ).filter(
        ServiceType.name == service_name
    ).first()

    if not existing:

        db.add(
            ServiceType(
                name=service_name
            )
        )

db.commit()
db.close()

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

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == False
    ).all()

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
# --------------------------------------------------
# Edit Vehicle Page
# --------------------------------------------------

@app.get(
    "/vehicle-edit/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_edit_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_edit.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Edit Vehicle Submit
# --------------------------------------------------

@app.post(
    "/vehicle-edit/{vehicle_id}"
)
def vehicle_edit_submit(

    vehicle_id: int,

    nickname: str = Form(...),

    year: int = Form(...),

    make: str = Form(...),

    model: str = Form(...),

    trim: str = Form(...),

    vin: str = Form(...),

    current_mileage: int = Form(...)

):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.nickname = nickname
    vehicle.year = year
    vehicle.make = make
    vehicle.model = model
    vehicle.trim = trim
    vehicle.vin = vin
    vehicle.current_mileage = current_mileage

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/vehicle/{vehicle_id}",
        status_code=303
    )
# --------------------------------------------------
# Archive Vehicle Page
# --------------------------------------------------

@app.get(
    "/vehicle-archive/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_archive_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_archive.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Archive Vehicle Submit
# --------------------------------------------------

@app.post(
    "/vehicle-archive/{vehicle_id}"
)
def vehicle_archive_submit(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.archived = True

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )
# --------------------------------------------------
# Archived Vehicles
# --------------------------------------------------

@app.get(
    "/vehicles-archived",
    response_class=HTMLResponse
)
def archived_vehicles(
    request: Request
):

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == True
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicles_archived.html",
        context={
            "request": request,
            "vehicles": vehicles
        }
    )
# --------------------------------------------------
# Restore Vehicle Page
# --------------------------------------------------

@app.get(
    "/vehicle-restore/{vehicle_id}",
    response_class=HTMLResponse
)
def vehicle_restore_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicle_restore.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
@app.post(
    "/vehicle-restore/{vehicle_id}"
)
def vehicle_restore_submit(
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    vehicle.archived = False

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )
@app.get(
    "/vendors-ui",
    response_class=HTMLResponse
)
def vendors_ui(
    request: Request
):

    db = SessionLocal()

    vendors = db.query(
        Vendor
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendors.html",
        context={
            "request": request,
            "vendors": vendors
        }
    )
@app.get(
    "/vendor-add",
    response_class=HTMLResponse
)
def vendor_add_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="vendor_add.html",
        context={
            "request": request
        }
    )
@app.post(
    "/vendor-add"
)
def vendor_add_submit(

    name: str = Form(...),

    address_1: str = Form(""),

    phone: str = Form(""),

    website: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    vendor = Vendor(

        name=name,

        address_1=address_1,

        phone=phone,

        website=website,

        notes=notes

    )


    db.add(vendor)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/vendors-ui",
        status_code=303
    )
# --------------------------------------------------
# Vendor Detail
# --------------------------------------------------

@app.get(
    "/vendor/{vendor_id}",
    response_class=HTMLResponse
)
def vendor_detail(
    request: Request,
    vendor_id: int
):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_detail.html",
        context={
            "request": request,
            "vendor": vendor
        }
    )
# --------------------------------------------------
# Edit Vendor Page
# --------------------------------------------------

@app.get(
    "/vendor-edit/{vendor_id}",
    response_class=HTMLResponse
)
def vendor_edit_page(
    request: Request,
    vendor_id: int
):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_edit.html",
        context={
            "request": request,
            "vendor": vendor
        }
    )
# --------------------------------------------------
# Edit Vendor Submit
# --------------------------------------------------

@app.post(
    "/vendor-edit/{vendor_id}"
)
def vendor_edit_submit(

    vendor_id: int,

    name: str = Form(...),

    address_1: str = Form(""),

    phone: str = Form(""),

    website: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    vendor.name = name
    vendor.address_1 = address_1
    vendor.phone = phone
    vendor.website = website
    vendor.notes = notes

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/vendor/{vendor_id}",
        status_code=303
    )
# --------------------------------------------------
# Maintenance List
# --------------------------------------------------

@app.get(
    "/maintenance-ui",
    response_class=HTMLResponse
)
def maintenance_ui(
    request: Request
):

    db = SessionLocal()

    visits = db.query(
        MaintenanceVisit
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance.html",
        context={
            "request": request,
            "visits": visits
        }
    )
# --------------------------------------------------
# Add Maintenance Visit Page
# --------------------------------------------------

@app.get(
    "/maintenance-add",
    response_class=HTMLResponse
)
def maintenance_add_page(
    request: Request
):

    db = SessionLocal()

    vehicles = db.query(
        Vehicle
    ).filter(
        Vehicle.archived == False
    ).all()

    vendors = db.query(
        Vendor
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_add.html",
        context={
            "request": request,
            "vehicles": vehicles,
            "vendors": vendors
        }
    )
# --------------------------------------------------
# Add Maintenance Visit Submit
# --------------------------------------------------

@app.post(
    "/maintenance-add"
)
def maintenance_add_submit(

    vehicle_id: int = Form(...),

    vendor_id: int = Form(...),

    visit_date: str = Form(...),

    mileage: int = Form(...),

    invoice_number: str = Form(""),

    total_cost: float = Form(0)

):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    visit = MaintenanceVisit(

        vehicle_id=vehicle_id,

        vendor=vendor.name,

        visit_date=visit_date,

        mileage=mileage,

        invoice_number=invoice_number,

        total_cost=total_cost

    )

    db.add(visit)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/maintenance-ui",
        status_code=303
    )
# --------------------------------------------------
# Edit Maintenance Visit
# --------------------------------------------------

@app.get(
    "/maintenance-edit/{visit_id}",
    response_class=HTMLResponse
)
def maintenance_edit_page(
    request: Request,
    visit_id: int
):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_edit.html",
        context={
            "request": request,
            "visit": visit
        }
    )
@app.post(
    "/maintenance-edit/{visit_id}"
)
def maintenance_edit_submit(

    visit_id: int,

    mileage: int = Form(...),

    invoice_number: str = Form(""),

    total_cost: float = Form(0)

):

    db = SessionLocal()

    visit = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.id == visit_id
    ).first()

    visit.mileage = mileage
    visit.invoice_number = invoice_number
    visit.total_cost = total_cost

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintenance-visit/{visit_id}",
        status_code=303
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
