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

 #
    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.archived == False
    ).all()
#
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
#
    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.archived == False
    ).all()
#

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
@router.put("/maintenance-schedule/{schedule_id}")
def update_maintenance_schedule(
    schedule_id: int,
    schedule_data: MaintenanceScheduleCreate
):

    db = SessionLocal()

    schedule = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()

    if not schedule:

        db.close()

        return {
            "error": "Schedule not found"
        }

    schedule.vehicle_id = schedule_data.vehicle_id

    schedule.service_type = schedule_data.service_type

    schedule.interval_miles = schedule_data.interval_miles

    schedule.interval_months = schedule_data.interval_months

    schedule.estimated_cost = schedule_data.estimated_cost

    schedule.uses_health_indicator = (
        schedule_data.uses_health_indicator
    )

    schedule.notes = schedule_data.notes

    db.commit()

    db.close()

    return {
        "message": "Maintenance schedule updated"
    }
@router.put("/maintenance-schedule/{schedule_id}/archive")
def archive_maintenance_schedule(schedule_id: int):

    db = SessionLocal()

    schedule = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()

    if not schedule:
        db.close()
        return {"error": "Schedule not found"}

    schedule.archived = True

    db.commit()
    db.close()

    return {
        "message": "Maintenance schedule archived"
    }
@router.put("/maintenance-schedule/{schedule_id}/restore")
def restore_maintenance_schedule(schedule_id: int):

    db = SessionLocal()

    schedule = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()

    if not schedule:
        db.close()
        return {"error": "Schedule not found"}

    schedule.archived = False

    db.commit()
    db.close()

    return {
        "message": "Maintenance schedule restored"
    }