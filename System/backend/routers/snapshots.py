from fastapi import APIRouter

from schemas.snapshot import SnapshotCreate
from database import SessionLocal
from models import Snapshot

router = APIRouter()


@router.get("/snapshots")
def get_snapshots():

    db = SessionLocal()

    snapshots = db.query(Snapshot).all()

    results = []

    for snapshot in snapshots:
        results.append({
            "id": snapshot.id,
            "timestamp": snapshot.timestamp,
            "action": snapshot.action,
            "description": snapshot.description,
            "vehicle_id": snapshot.vehicle_id
        })

    db.close()

    return results


@router.post("/snapshots")
def create_snapshot(snapshot: SnapshotCreate):

    db = SessionLocal()

    new_snapshot = Snapshot(
        timestamp=snapshot.timestamp,
        action=snapshot.action,
        description=snapshot.description,
        vehicle_id=snapshot.vehicle_id
    )

    db.add(new_snapshot)
    db.commit()
    db.refresh(new_snapshot)

    db.close()

    return {
        "message": "Snapshot created",
        "id": new_snapshot.id
    }