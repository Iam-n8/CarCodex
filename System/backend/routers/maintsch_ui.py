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

    default_items = [
        {
            "item_name": "Oil Change",
            "service_type_match": "Oil Change",
            "miles_interval": 5000,
            "period_months": 6,
            "notes": "Default oil change interval. Owner may adjust.",
            "display_order": 10
        },
        {
            "item_name": "Tire Rotation",
            "service_type_match": "Tire Rotation",
            "miles_interval": 5000,
            "period_months": 6,
            "notes": "Rotate tires to support even tread wear.",
            "display_order": 20
        },
        {
            "item_name": "Check Brakes",
            "service_type_match": "Brake Inspection",
            "miles_interval": 10000,
            "period_months": 12,
            "notes": "Inspect pads, rotors, calipers, and brake lines.",
            "display_order": 30
        },
        {
            "item_name": "Replace Engine Air Filter",
            "service_type_match": "Engine Air Filter",
            "miles_interval": 30000,
            "period_months": 24,
            "notes": "Replace more often in dusty conditions.",
            "display_order": 40
        },
        {
            "item_name": "Replace Cabin Air Filter",
            "service_type_match": "Cabin Air Filter",
            "miles_interval": 30000,
            "period_months": 24,
            "notes": "Replace for clean interior airflow.",
            "display_order": 50
        },
        {
            "item_name": "Replace Brake Fluid",
            "service_type_match": "Brake Fluid",
            "miles_interval": None,
            "period_months": 60,
            "notes": "Time-based default. Manufacturer intervals may vary.",
            "display_order": 60
        },
        {
            "item_name": "Coolant Service",
            "service_type_match": "Coolant Service",
            "miles_interval": 60000,
            "period_months": 60,
            "notes": "Inspect coolant condition and service as needed.",
            "display_order": 70
        },
        {
            "item_name": "Transmission Fluid Service",
            "service_type_match": "Transmission Fluid",
            "miles_interval": 60000,
            "period_months": 60,
            "notes": "Interval varies by manufacturer and usage.",
            "display_order": 80
        },
        {
            "item_name": "Replace Spark Plugs",
            "service_type_match": "Spark Plugs",
            "miles_interval": 100000,
            "period_months": None,
            "notes": "Mileage-based default. Confirm manufacturer interval.",
            "display_order": 90
        },
        {
            "item_name": "Inspect Belts and Hoses",
            "service_type_match": "Belts and Hoses",
            "miles_interval": 60000,
            "period_months": 48,
            "notes": "Inspect serpentine belt, accessory belts, and hoses.",
            "display_order": 100
        }
    ]

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
# Add Maintenance Schedule Item Submit
# --------------------------------------------------

@router.post(
    "/maintsch-ui/{vehicle_id}/add"
)
def maintsch_add_item_submit(

    vehicle_id: int,

    item_name: str = Form(""),

    service_type_match: str = Form(""),

    miles_interval: int | None = Form(None),

    period_months: int | None = Form(None),

    notes: str = Form(""),

    display_order: int = Form(0)

):

    if not item_name.strip():

        item_name = "Schedule Item"

    if not service_type_match.strip():

        service_type_match = item_name

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

    db = SessionLocal()

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

