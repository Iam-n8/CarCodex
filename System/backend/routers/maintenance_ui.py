# maintenance_ui.py

from models import (
    MaintenanceVisit,
    ServiceRecord
)
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
    MaintenanceVisit
)

from database import SessionLocal

router = APIRouter()

# --------------------------------------------------
# Maintenance List
# --------------------------------------------------

@router.get(
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




# --------------------------------------------------
# Vehicle Maintenance Add Page
# --------------------------------------------------
@router.get(
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

@router.post(
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

@router.get(
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
@router.post(
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