# maintenance_schedule.py

from fastapi import APIRouter

from database import SessionLocal
from models import MaintenanceSchedule

from schemas.maintenance_schedule import (
    MaintenanceScheduleCreate
)

router = APIRouter()


@router.get("/maintenance-schedule")
def get_maintenance_schedule():

    db = SessionLocal()

    schedules = db.query(
        MaintenanceSchedule
    ).all()

    results = []

    for schedule in schedules:

        results.append({
            "id": schedule.id,
            "vehicle_id": schedule.vehicle_id,
            "service_type": schedule.service_type,
            "interval_miles": schedule.interval_miles,
            "interval_months": schedule.interval_months,
            "estimated_cost": schedule.estimated_cost,
            "uses_health_indicator":
                schedule.uses_health_indicator
        })

    db.close()

    return results


@router.post("/maintenance-schedule")
def create_maintenance_schedule(
    schedule: MaintenanceScheduleCreate
):

    db = SessionLocal()

    new_schedule = MaintenanceSchedule(
        vehicle_id=schedule.vehicle_id,
        service_type=schedule.service_type,
        interval_miles=schedule.interval_miles,
        interval_months=schedule.interval_months,
        estimated_cost=schedule.estimated_cost,
        uses_health_indicator=
            schedule.uses_health_indicator,
        notes=schedule.notes
    )

    db.add(new_schedule)

    db.commit()

    db.refresh(new_schedule)

    db.close()
@router.get("/maintenance-schedule/{vehicle_id}")

def get_vehicle_maintenance_schedule(
    vehicle_id: int
):

    db = SessionLocal()

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()

    results = []

    for schedule in schedules:

        results.append({
            "id": schedule.id,
            "service_type": schedule.service_type,
            "interval_miles": schedule.interval_miles,
            "interval_months": schedule.interval_months,
            "estimated_cost": schedule.estimated_cost,
            "uses_health_indicator":
                schedule.uses_health_indicator,
            "notes": schedule.notes
        })

    db.close()

    return results

    return {
        "message": "Maintenance schedule added",
        "id": new_schedule.id
    }