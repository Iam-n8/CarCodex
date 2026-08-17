# --------------------------------------------------
# maintenance_due.py
#
# Maintenance Due Calculation Helpers
#
# Purpose:
# - Keep Maintenance Due logic separate from UI routers
# - Connect MaintSch schedule items to completed services
# - Use Primary Service and Additional Services equally
# - Calculate service due status and service progress
# --------------------------------------------------

from datetime import datetime
from datetime import date

from models import (
    Vehicle,
    MaintenanceVisit,
    ServiceRecord,
    MaintenanceSchedule
)


# --------------------------------------------------
# Normalize Service Names
# --------------------------------------------------

def normalize_service_name(
    value
):
    """
    Normalize a service name for matching.

    Example:
    " Oil Change " -> "oil change"
    """

    if not value:

        return ""

    return value.strip().lower()


# --------------------------------------------------
# Split Additional Services
# --------------------------------------------------

def split_additional_services(
    additional_services
):
    """
    Additional services are stored as text.

    Example:
    Tire Rotation
    Cabin Air Filter
    Multi-Point Inspection

    Return a clean list of service names.
    """

    if not additional_services:

        return []

    services = []

    lines = additional_services.replace(
        "\r",
        ""
    ).split(
        "\n"
    )

    for line in lines:

        service_name = line.strip()

        if service_name:

            services.append(
                service_name
            )

    return services


# --------------------------------------------------
# Parse Date
# --------------------------------------------------

def parse_date(
    value
):
    """
    Convert a stored date string into a date object.

    Expected format:
    YYYY-MM-DD
    """

    if not value:

        return None

    try:

        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except Exception:

        return None


# --------------------------------------------------
# Add Months
# --------------------------------------------------

def add_months(
    start_date,
    months
):
    """
    Add months to a date.
    """

    if not start_date or not months:

        return None

    month = start_date.month - 1 + months

    year = start_date.year + month // 12

    month = month % 12 + 1

    day = min(
        start_date.day,
        28
    )

    return date(
        year,
        month,
        day
    )


# --------------------------------------------------
# Percent Helpers
# --------------------------------------------------

def clamp_percent(
    value
):
    """
    Keep percentage values in a readable range.
    """

    if value is None:

        return None

    if value < 0:

        return 0

    if value > 100:

        return 100

    return round(
        value,
        1
    )


def calculate_mileage_percent_used(
    last_mileage,
    current_mileage,
    miles_interval
):
    """
    Calculate how much of the mileage interval has been used.
    """

    if (
        last_mileage is None
        or current_mileage is None
        or not miles_interval
    ):

        return None

    miles_used = (
        current_mileage
        - last_mileage
    )

    if miles_used < 0:

        miles_used = 0

    percent_used = (
        miles_used
        / miles_interval
    ) * 100

    return clamp_percent(
        percent_used
    )


def calculate_time_percent_used(
    last_date,
    period_months
):
    """
    Calculate how much of the time interval has been used.
    """

    if (
        not last_date
        or not period_months
    ):

        return None

    today = date.today()

    days_used = (
        today
        - last_date
    ).days

    if days_used < 0:

        days_used = 0

    months_used = (
        days_used
        / 30
    )

    percent_used = (
        months_used
        / period_months
    ) * 100

    return clamp_percent(
        percent_used
    )


def calculate_overall_service_progress(
    mileage_percent_used,
    time_percent_used
):
    """
    Use the highest percent used because maintenance is due
    when either mileage or time reaches the interval.
    """

    available_values = []

    if mileage_percent_used is not None:

        available_values.append(
            {
                "basis": "Mileage",
                "percent_used": mileage_percent_used
            }
        )

    if time_percent_used is not None:

        available_values.append(
            {
                "basis": "Time",
                "percent_used": time_percent_used
            }
        )

    if not available_values:

        return {
            "percent_used": None,
            "percent_remaining": None,
            "due_basis": "Unknown"
        }

    if (
        mileage_percent_used is not None
        and time_percent_used is not None
        and mileage_percent_used == time_percent_used
    ):

        due_basis = "Mileage/Time"

        percent_used = mileage_percent_used

    else:

        highest = max(
            available_values,
            key=lambda item: item["percent_used"]
        )

        due_basis = highest["basis"]

        percent_used = highest["percent_used"]

    percent_remaining = (
        100
        - percent_used
    )

    if percent_remaining < 0:

        percent_remaining = 0

    return {
        "percent_used": percent_used,
        "percent_remaining": round(
            percent_remaining,
            1
        ),
        "due_basis": due_basis
    }


# --------------------------------------------------
# Highest Known Vehicle Mileage
# --------------------------------------------------

def get_highest_known_mileage(
    db,
    vehicle_id: int
):
    """
    Return the highest mileage known for a vehicle.

    Looks at:
    - Vehicle.current_mileage
    - MaintenanceVisit.mileage
    """

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()

    highest_mileage = 0

    if vehicle and vehicle.current_mileage:

        highest_mileage = vehicle.current_mileage

    visits = db.query(
        MaintenanceVisit
    ).filter(
        MaintenanceVisit.vehicle_id == vehicle_id
    ).all()

    for visit in visits:

        if (
            visit.mileage is not None
            and visit.mileage > highest_mileage
        ):

            highest_mileage = visit.mileage

    return highest_mileage


# --------------------------------------------------
# Completed Service Entries
# --------------------------------------------------

def get_completed_service_entries(
    db,
    vehicle_id: int
):
    """
    Build a flat list of completed service entries.

    A single Maintenance Visit can count as multiple services:

    Primary Service:
        Oil Change

    Additional Services:
        Tire Rotation
        Cabin Air Filter
    """

    records = db.query(
        ServiceRecord
    ).filter(
        ServiceRecord.vehicle_id == vehicle_id,
        ServiceRecord.archived == False
    ).all()

    entries = []

    for record in records:

        if (
            record.service_status
            and record.service_status != "COMPLETED"
        ):

            continue

        visit = None

        if record.maintenance_visit_id:

            visit = db.query(
                MaintenanceVisit
            ).filter(
                MaintenanceVisit.id == record.maintenance_visit_id
            ).first()

        service_date = record.service_date

        service_mileage = record.mileage

        if visit:

            service_date = visit.visit_date

            service_mileage = visit.mileage

        if record.primary_reason:

            entries.append(
                {
                    "service_name": record.primary_reason,
                    "service_name_normalized": normalize_service_name(
                        record.primary_reason
                    ),
                    "source": "primary",
                    "service_record_id": record.id,
                    "maintenance_visit_id": record.maintenance_visit_id,
                    "service_date": service_date,
                    "mileage": service_mileage
                }
            )

        additional_services = split_additional_services(
            record.additional_services
        )

        for additional_service in additional_services:

            entries.append(
                {
                    "service_name": additional_service,
                    "service_name_normalized": normalize_service_name(
                        additional_service
                    ),
                    "source": "additional",
                    "service_record_id": record.id,
                    "maintenance_visit_id": record.maintenance_visit_id,
                    "service_date": service_date,
                    "mileage": service_mileage
                }
            )

    return entries


# --------------------------------------------------
# Find Last Completed Matching Service
# --------------------------------------------------

def find_last_completed_service(
    db,
    vehicle_id: int,
    service_type_match: str
):
    """
    Find the most recent completed service that matches
    a MaintSch service_type_match value.
    """

    match_name = normalize_service_name(
        service_type_match
    )

    if not match_name:

        return None

    entries = get_completed_service_entries(
        db,
        vehicle_id
    )

    matches = []

    for entry in entries:

        if entry["service_name_normalized"] == match_name:

            matches.append(
                entry
            )

    if not matches:

        return None

    matches.sort(
        key=lambda entry: (
            entry["mileage"] or 0,
            entry["service_date"] or ""
        ),
        reverse=True
    )

    return matches[0]


# --------------------------------------------------
# Calculate One Schedule Item
# --------------------------------------------------

def calculate_schedule_item_due(
    db,
    vehicle_id: int,
    schedule,
    due_soon_miles: int = 1000,
    due_soon_months: int = 2
):
    """
    Calculate due status for one MaintSch item.
    """

    current_mileage = get_highest_known_mileage(
        db,
        vehicle_id
    )

    last_service = find_last_completed_service(
        db,
        vehicle_id,
        schedule.service_type_match
    )

    if not last_service:

        return {
            "schedule_id": schedule.id,
            "item_name": schedule.item_name,
            "service_type_match": schedule.service_type_match,
            "status": "NO HISTORY",
            "last_date": None,
            "last_mileage": None,
            "miles_due": None,
            "miles_to_go": None,
            "date_due": None,
            "months_to_go": None,
            "current_mileage": current_mileage,
            "mileage_percent_used": None,
            "time_percent_used": None,
            "percent_used": None,
            "percent_remaining": None,
            "due_basis": "No History",
            "notes": schedule.notes
        }

    last_mileage = last_service.get(
        "mileage"
    )

    last_date_text = last_service.get(
        "service_date"
    )

    last_date = parse_date(
        last_date_text
    )

    miles_due = None

    miles_to_go = None

    date_due = None

    months_to_go = None

    mileage_overdue = False

    date_overdue = False

    mileage_due_soon = False

    date_due_soon = False

    mileage_percent_used = None

    time_percent_used = None

    # ----------------------------------------------
    # Mileage-based calculation
    # ----------------------------------------------

    if (
        schedule.miles_interval
        and last_mileage is not None
    ):

        miles_due = (
            last_mileage
            + schedule.miles_interval
        )

        miles_to_go = (
            miles_due
            - current_mileage
        )

        mileage_percent_used = calculate_mileage_percent_used(
            last_mileage,
            current_mileage,
            schedule.miles_interval
        )

        if miles_to_go < 0:

            mileage_overdue = True

        elif miles_to_go <= due_soon_miles:

            mileage_due_soon = True

    # ----------------------------------------------
    # Time-based calculation
    # ----------------------------------------------

    if (
        schedule.period_months
        and last_date
    ):

        date_due_obj = add_months(
            last_date,
            schedule.period_months
        )

        if date_due_obj:

            date_due = date_due_obj.isoformat()

            today = date.today()

            days_to_go = (
                date_due_obj
                - today
            ).days

            months_to_go = int(
                days_to_go / 30
            )

            time_percent_used = calculate_time_percent_used(
                last_date,
                schedule.period_months
            )

            if days_to_go < 0:

                date_overdue = True

            elif days_to_go <= (
                due_soon_months * 30
            ):

                date_due_soon = True

    # ----------------------------------------------
    # Overall percent progress
    # ----------------------------------------------

    progress = calculate_overall_service_progress(
        mileage_percent_used,
        time_percent_used
    )

    # ----------------------------------------------
    # Status
    # ----------------------------------------------

    if (
        mileage_overdue
        or date_overdue
    ):

        status = "OVERDUE"

    elif (
        mileage_due_soon
        or date_due_soon
    ):

        status = "DUE SOON"

    else:

        status = "GOOD"

    return {
        "schedule_id": schedule.id,
        "item_name": schedule.item_name,
        "service_type_match": schedule.service_type_match,
        "status": status,
        "last_date": last_date_text,
        "last_mileage": last_mileage,
        "miles_due": miles_due,
        "miles_to_go": miles_to_go,
        "date_due": date_due,
        "months_to_go": months_to_go,
        "current_mileage": current_mileage,
        "mileage_percent_used": mileage_percent_used,
        "time_percent_used": time_percent_used,
        "percent_used": progress["percent_used"],
        "percent_remaining": progress["percent_remaining"],
        "due_basis": progress["due_basis"],
        "notes": schedule.notes
    }


# --------------------------------------------------
# Calculate Vehicle Maintenance Due
# --------------------------------------------------

def calculate_vehicle_maintenance_due(
    db,
    vehicle_id: int,
    due_soon_miles: int = 1000,
    due_soon_months: int = 2
):
    """
    Calculate Maintenance Due results for all active
    MaintSch items for a vehicle.
    """

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id,
        MaintenanceSchedule.inactive == False
    ).order_by(
        MaintenanceSchedule.display_order
    ).all()

    results = []

    for schedule in schedules:

        result = calculate_schedule_item_due(
            db,
            vehicle_id,
            schedule,
            due_soon_miles,
            due_soon_months
        )

        results.append(
            result
        )

    return results
