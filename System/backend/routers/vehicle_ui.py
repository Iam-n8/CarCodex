# Vehicle UI Routes

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

from database import SessionLocal

from models import (
    Vehicle,
    MaintenanceVisit,
    MaintenanceSchedule,
    Document
)

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)
@router.get(
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
@router.get(
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
# --------------------------------------------------
# Add Vehicle Page
# --------------------------------------------------

@router.get(
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

@router.post(
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