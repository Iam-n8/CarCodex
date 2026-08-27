from fastapi import APIRouter

from schemas.event import EventCreate
from database import SessionLocal
from models import Event

router = APIRouter()


@router.get("/events")
def get_events():

    db = SessionLocal()

    events = db.query(Event).all()

    results = []

    for event in events:
        results.append({
            "id": event.id,
            "vehicle_id": event.vehicle_id,
            "category": event.category,
            "event_type": event.event_type,
            "description": event.description,
            "location": event.location,
            "mileage": event.mileage,
            "cost": event.cost
        })

    db.close()

    return results


@router.post("/events")
def create_event(event: EventCreate):

    db = SessionLocal()

    new_event = Event(
        vehicle_id=event.vehicle_id,
        event_date=event.event_date,
        mileage=event.mileage,
        category=event.category,
        event_type=event.event_type,
        description=event.description,
        location=event.location,
        cost=event.cost
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    db.close()

    return {
        "message": "Event added",
        "id": new_event.id
    }