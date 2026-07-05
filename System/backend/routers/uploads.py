
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import Form
from database import SessionLocal
from models import Vehicle

from fastapi import File

import os
import shutil

router = APIRouter()


@router.post("/upload-test")
def upload_test(
    vehicle_id: int = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...)
):

    db = SessionLocal()

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id
    ).first()

    if not vehicle:
        db.close()

        return {
            "error": "Vehicle not found"
        }

    vehicle_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "Documents",
            f"VEH_{vehicle_id:06d}",
            category
        )
    )

    os.makedirs(
        vehicle_folder,
        exist_ok=True
    )

    destination = os.path.join(
        vehicle_folder,
        file.filename
    )

    print("Vehicle Folder:", vehicle_folder)
    print("Destination:", destination)

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    db.close()

    return {
        "message": "File saved",
        "vehicle_id": vehicle_id,
        "category": category,
        "filename": file.filename
    }