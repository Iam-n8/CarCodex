from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from database import SessionLocal
from models import Vehicle, Document

import os
import shutil

router = APIRouter()

ALLOWED_EXTENSIONS = [
    "pdf",
    "jpg",
    "jpeg",
    "png",
    "txt",
    "csv",
    "docx",
    "xlsx"
]


@router.post("/upload")
def upload_test(
    vehicle_id: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    upload_date: str = Form(...),
    file: UploadFile = File(...)
):

    db = SessionLocal()

    try:

        vehicle = db.query(Vehicle).filter(
            Vehicle.id == vehicle_id
        ).first()

        if not vehicle:
            
            extension = os.path.splitext(
                file.filename
            )[1].lower().replace(".", "")

            if extension not in ALLOWED_EXTENSIONS:
                db.close()

                return {
                    "error": f"File type '{extension}' not allowed"
                }

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

        extension = os.path.splitext(
            file.filename
        )[1]

        new_filename = (
            f"{vehicle.nickname}_"
            f"{category}_"
            f"{description}_"
            f"{upload_date}"
            f"{extension}"
        )

        new_filename = new_filename.replace(
            " ",
            "_"
        )

        destination = os.path.join(
            vehicle_folder,
            new_filename
        )

        print("Destination:", destination)

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        new_document = Document(
            vehicle_id=vehicle_id,
            document_type=category,
            file_name=new_filename,
            file_path=destination,
            upload_date=upload_date,
            notes=description
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        print("Document record created:", new_document.id)

        return {
            "message": "Document uploaded successfully",
            "document_id": new_document.id,
            "vehicle_id": vehicle_id,
            "category": category,
            "filename": new_filename

        }

    finally:
        db.close()