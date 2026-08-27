from fastapi import APIRouter
from datetime import datetime
from datetime import datetime, timedelta
from database import SessionLocal

from models import (
    Vehicle,
    ServiceRecord,
    MaintenanceSchedule
)


from datetime import timedelta
from models import MaintenanceSchedule


router = APIRouter()


@router.get("/maintenance-due")

def maintenance_due():

    db = SessionLocal()

    vehicles = db.query(Vehicle).all()

    results = []

    today = datetime.today()

    for vehicle in vehicles:

        services = db.query(ServiceRecord).filter(
            ServiceRecord.vehicle_id == vehicle.id
        ).all()

        for service in services:

            remaining_miles = None

            if service.next_service_mileage:
                remaining_miles = (
                    service.next_service_mileage
                    - vehicle.current_mileage
                )

            remaining_days = None

            if service.next_service_date:

                try:

                    next_date = datetime.strptime(
                        service.next_service_date,
                        "%Y-%m-%d"
                    )

                    remaining_days = (
                        next_date - today
                    ).days

                except:
                    pass

            status = "OK"

            if (
                remaining_miles is not None
                and remaining_miles <= 0
            ):
                status = "OVERDUE"

            if (
                remaining_days is not None
                and remaining_days <= 0
            ):
                status = "OVERDUE"

            if status != "OVERDUE":

                if (
                    remaining_miles is not None
                    and remaining_miles <= 1000
                ):
                    status = "DUE_SOON"

                if (
                    remaining_days is not None
                    and remaining_days <= 30
                ):
                    status = "DUE_SOON"

            results.append({
                "vehicle": vehicle.nickname,
                "service": service.service_type,
                "current_mileage": vehicle.current_mileage,
                "next_service_mileage": service.next_service_mileage,
                "remaining_miles": remaining_miles,
                "next_service_date": service.next_service_date,
                "remaining_days": remaining_days,
                "status": status
            })
@router.get("/maintenance-status/{vehicle_id}")
def maintenance_status(vehicle_id: int):

    db = SessionLocal()

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:
        db.close()

        return {
            "error": "Vehicle not found"
        }

    schedules = db.query(
        MaintenanceSchedule
    ).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).all()

    results = []

    for schedule in schedules:

        last_service = db.query(
            ServiceRecord
        ).filter(
            ServiceRecord.vehicle_id == vehicle_id,
            ServiceRecord.service_type == schedule.service_type
        ).order_by(
            ServiceRecord.id.desc()
        ).first()

        status = "NO_HISTORY"

        last_service_date = None
        next_due_date = None

        if last_service:

            last_service_date = last_service.service_date

            try:

                service_date = datetime.strptime(
                    last_service.service_date,
                    "%Y-%m-%d"
                )

                if schedule.interval_months:

                    next_due_date = (
                        service_date +
                        timedelta(
                            days=schedule.interval_months * 30
                        )
                    ).strftime("%Y-%m-%d")

            except:
                pass

            status = "OK"

        results.append({
            "service": schedule.service_type,
            "last_service_date": last_service_date,
            "next_due_date": next_due_date,
            "estimated_cost": schedule.estimated_cost,
            "health_indicator":
                schedule.uses_health_indicator,
            "status": status
        })

    db.close()

    return results