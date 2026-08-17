# --------------------------------------------------
# maintsch_ui.py
#
# Maintenance Schedule UI Module
#
# Purpose:
# - Own the vehicle-specific maintenance schedule items
# - Stay separate from vehicle_ui.py
# - Provide the base item values that Maintenance Due
#   will calculate from later
# --------------------------------------------------

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

from database import (
    SessionLocal
)

from models import (
    MaintenanceSchedule,
    Vehicle
)
from helpers.maintenance_due import (
    calculate_vehicle_maintenance_due
)
from helpers.service_catalog_loader import (
    load_maintenance_trackable_rows,
    clean_csv_value,
    csv_int
)



router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)



# --------------------------------------------------
# Vehicle Maintenance Schedule Items
# --------------------------------------------------

@router.get(
    "/maintsch/{vehicle_id}"
)
def maintsch_vehicle_schedule(
    vehicle_id: int
):

    db = SessionLocal()

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).order_by(
        MaintenanceSchedule.display_order
    ).all()

    results = []

    for schedule in schedules:

        results.append(
            {
                "id": schedule.id,
                "vehicle_id": schedule.vehicle_id,
                "item_name": schedule.item_name,
                "service_type_match": schedule.service_type_match,
                "miles_interval": schedule.miles_interval,
                "period_months": schedule.period_months,
                "inactive": schedule.inactive,
                "notes": schedule.notes,
                "display_order": schedule.display_order
            }
        )

    db.close()

    return results


# --------------------------------------------------
# Seed Default Maintenance Schedule
# --------------------------------------------------

@router.post(
    "/maintsch/{vehicle_id}/seed-defaults"
)
def seed_default_maintenance_schedule(
    vehicle_id: int
):

    db = SessionLocal()

    existing_items = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()

    if existing_items:

        db.close()

        return RedirectResponse(
            url=f"/maintsch-ui/{vehicle_id}",
            status_code=303
        )

    catalog_rows = load_maintenance_trackable_rows()

    for item in default_items:

        schedule = MaintenanceSchedule(

            vehicle_id=vehicle_id,

            item_name=item["item_name"],

            service_type_match=item["service_type_match"],

            miles_interval=item["miles_interval"],

            period_months=item["period_months"],

            inactive=False,

            notes=item["notes"],

            display_order=item["display_order"]

        )

        db.add(
            schedule
        )

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintsch-ui/{vehicle_id}",
        status_code=303
    )
# --------------------------------------------------
# Vehicle Maintenance Schedule UI Page
# --------------------------------------------------

@router.get(
    "/maintsch-ui/{vehicle_id}",
    response_class=HTMLResponse
)
def maintsch_vehicle_schedule_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).order_by(
        MaintenanceSchedule.display_order
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintsch.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "schedules": schedules
        }
    )
# --------------------------------------------------
# Add Maintenance Schedule Item Page
# --------------------------------------------------

@router.get(
    "/maintsch-ui/{vehicle_id}/add",
    response_class=HTMLResponse
)
def maintsch_add_item_page(
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
        name="maintsch_add.html",
        context={
            "request": request,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Seed Default Maintenance Schedule
# --------------------------------------------------

@router.post(
    "/maintsch/{vehicle_id}/seed-defaults"
)
def seed_default_maintenance_schedule(
    vehicle_id: int
):

    db = SessionLocal()

    existing_items = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()

    if existing_items:

        db.close()

        return RedirectResponse(
            url=f"/maintsch-ui/{vehicle_id}",
            status_code=303
        )

    catalog_rows = load_maintenance_trackable_rows()

    items_created = 0

    for row in catalog_rows:

        item_name = clean_csv_value(
            row.get(
                "service_item"
            )
        )

        service_type_match = clean_csv_value(
            row.get(
                "service_type_match"
            )
        )

        miles_interval = csv_int(
            row.get(
                "default_miles_interval"
            ),
            default=0
        )

        period_months = csv_int(
            row.get(
                "default_period_months"
            ),
            default=0
        )

        display_order = csv_int(
            row.get(
                "service_code"
            ),
            default=0
        )

        notes = clean_csv_value(
            row.get(
                "notes"
            )
        )

        if not item_name:

            continue

        if not service_type_match:

            service_type_match = item_name

        if miles_interval == 0:

            miles_interval = None

        if period_months == 0:

            period_months = None

        schedule = MaintenanceSchedule(

            vehicle_id=vehicle_id,

            item_name=item_name,

            service_type_match=service_type_match,

            miles_interval=miles_interval,

            period_months=period_months,

            inactive=False,

            notes=notes,

            display_order=display_order

        )

        db.add(
            schedule
        )

        items_created += 1

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintsch-ui/{vehicle_id}",
        status_code=303
    )
# --------------------------------------------------
# Edit Maintenance Schedule Item Page
# --------------------------------------------------

@router.get(
    "/maintsch-ui/item/{schedule_id}/edit",
    response_class=HTMLResponse
)
def maintsch_edit_item_page(
    request: Request,
    schedule_id: int
):

    db = SessionLocal()

    schedule = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == schedule.vehicle_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintsch_edit.html",
        context={
            "request": request,
            "schedule": schedule,
            "vehicle": vehicle
        }
    )
# --------------------------------------------------
# Edit Maintenance Schedule Item Submit
# --------------------------------------------------

@router.post(
    "/maintsch-ui/item/{schedule_id}/edit"
)
def maintsch_edit_item_submit(

    schedule_id: int,

    item_name: str = Form(""),

    service_type_match: str = Form(""),

    miles_interval: int | None = Form(None),

    period_months: int | None = Form(None),

    inactive: str = Form(""),

    notes: str = Form(""),

    display_order: int = Form(0)

):

    db = SessionLocal()

    schedule = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()

    if not schedule:

        db.close()

        return RedirectResponse(
            url="/vehicles-ui",
            status_code=303
        )

    if not item_name.strip():

        item_name = "Schedule Item"

    if not service_type_match.strip():

        service_type_match = item_name

    schedule.item_name = item_name

    schedule.service_type_match = service_type_match

    schedule.miles_interval = miles_interval

    schedule.period_months = period_months

    schedule.inactive = (
        inactive == "on"
    )

    schedule.notes = notes

    schedule.display_order = display_order

    vehicle_id = schedule.vehicle_id

    db.commit()

    db.close()

    return RedirectResponse(
        url=f"/maintsch-ui/{vehicle_id}",
        status_code=303
    )

# --------------------------------------------------
# Maintenance Due UI Page
# --------------------------------------------------

@router.get(
    "/maintenance-due-ui/{vehicle_id}",
    response_class=HTMLResponse
)
def maintenance_due_vehicle_page(
    request: Request,
    vehicle_id: int
):

    db = SessionLocal()

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    due_items = calculate_vehicle_maintenance_due(
        db,
        vehicle_id
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="maintenance_due.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "due_items": due_items
        }
    )