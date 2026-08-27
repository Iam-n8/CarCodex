# vendor_ui.py

import os

print(
    "VENDOR DETAIL TEMPLATE:",
    os.path.abspath(
        os.path.join(
            "templates",
            "vendor_detail.html"
        )
    )
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
    Vendor,
    Vehicle,
    MaintenanceVisit,
    ServiceRecord
)
from helpers.service_catalog_loader import (
    load_available_domains
)

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)




# --------------------------------------------------
# Vendor Detail
# --------------------------------------------------

@router.get(
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

    if not vendor:

        db.close()

        return RedirectResponse(
            url="/vendors-ui",
            status_code=303
        )

    visits = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.vendor_id == vendor_id,
        MaintenanceVisit.archived == False
    ).order_by(
        MaintenanceVisit.visit_date.desc()
    ).all()

    visit_history = []

    total_spent = 0.0

    vehicle_ids = set()

    for visit in visits:

        vehicle = db.query(
            Vehicle
        ).filter(
            Vehicle.id == visit.vehicle_id
        ).first()

        service = db.query(
            ServiceRecord
        ).filter(
            ServiceRecord.maintenance_visit_id == visit.id
        ).first()

        if visit.total_cost is not None:

            total_spent += visit.total_cost

        if visit.vehicle_id is not None:

            vehicle_ids.add(
                visit.vehicle_id
            )

        visit_history.append(
            {
                "visit": visit,
                "vehicle": vehicle,
                "service": service
            }
        )

    last_visit = None

    if visits:

        last_visit = visits[0]

    visit_count = len(
        visits
    )

    vehicles_serviced_count = len(
        vehicle_ids
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_detail.html",
        context={
            "request": request,
            "vendor": vendor,
            "visit_history": visit_history,
            "visit_count": visit_count,
            "total_spent": total_spent,
            "last_visit": last_visit,
            "vehicles_serviced_count": (
                vehicles_serviced_count
            )
        }
    )

# --------------------------------------------------
# Edit Vendor Page
# --------------------------------------------------

@router.get(
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

    if not vendor:

        db.close()

        return RedirectResponse(
            url="/vendors-ui",
            status_code=303
        )

    available_domains = load_available_domains()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="vendor_edit.html",
        context={
            "request": request,
            "vendor": vendor,
            "available_domains": available_domains
        }
    )

# --------------------------------------------------
# Edit Vendor Submit
# --------------------------------------------------

@router.post(
    "/vendor-edit/{vendor_id}"
)
def vendor_edit_submit(

    vendor_id: int,

    name: str = Form(...),

    vendor_type: str = Form(""),

    domain: str = Form(""),

    rating: int | None = Form(None),

    address_1: str = Form(""),

    address_2: str = Form(""),

    city: str = Form(""),

    state: str = Form(""),

    zip_code: str = Form(""),

    primary_contact: str = Form(""),

    phone: str = Form(""),

    email: str = Form(""),

    website: str = Form(""),

    is_preferred: str = Form(""),

    notes: str = Form("")

):

    db = SessionLocal()

    vendor = db.query(
        Vendor
    ).filter(
        Vendor.id == vendor_id
    ).first()

    if not vendor:

        db.close()

        return RedirectResponse(
            url="/vendors-ui",
            status_code=303
        )

    # ----------------------------------------------
    # Clean Values
    # ----------------------------------------------

    name = name.strip()

    vendor_type = vendor_type.strip()

    domain = domain.strip()

    address_1 = address_1.strip()

    address_2 = address_2.strip()

    city = city.strip()

    state = state.strip().upper()

    zip_code = zip_code.strip()

    primary_contact = primary_contact.strip()

    phone = phone.strip()

    email = email.strip()

    website = website.strip()

    notes = notes.strip()

    if not name:

        name = "Vendor Name Unknown"

    if (
        rating is not None
        and rating not in [
            1,
            2,
            3,
            4,
            5
        ]
    ):

        rating = None

    # ----------------------------------------------
    # Update Vendor
    # ----------------------------------------------

    vendor.name = name

    vendor.vendor_type = (
        vendor_type
        if vendor_type
        else None
    )

    vendor.domain = (
        domain
        if domain
        else None
    )

    vendor.rating = rating

    vendor.address_1 = (
        address_1
        if address_1
        else None
    )

    vendor.address_2 = (
        address_2
        if address_2
        else None
    )

    vendor.city = (
        city
        if city
        else None
    )

    vendor.state = (
        state
        if state
        else None
    )

    vendor.zip_code = (
        zip_code
        if zip_code
        else None
    )

    vendor.primary_contact = (
        primary_contact
        if primary_contact
        else None
    )

    vendor.phone = (
        phone
        if phone
        else None
    )

    vendor.email = (
        email
        if email
        else None
    )

    vendor.website = (
        website
        if website
        else None
    )

    vendor.is_preferred = (
        is_preferred == "on"
    )

    vendor.notes = (
        notes
        if notes
        else None
    )

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/vendor/{vendor_id}",
        status_code=303
    )
