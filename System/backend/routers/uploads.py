# uploads.py

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from database import SessionLocal
from models import Vehicle, Document

import os
import shutil

from helpers.storage import (
    save_document_file
)


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


@router.post("/documents/upload")
def upload(
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
            return {
                "error": "Vehicle not found"
            }

        extension = os.path.splitext(
            file.filename
        )[1].lower().replace(".", "")

        if extension not in ALLOWED_EXTENSIONS:
            return {
                "error": f"File type '{extension}' not allowed"
            }

        new_document = Document(
            vehicle_id=vehicle_id,
            document_type=category,
            upload_date=upload_date,
            notes=description
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        destination = save_document_file(
            vehicle,
            category,
            upload_date,
            new_document.id,
            file
        )

        new_document.file_path = destination

        new_document.file_name = os.path.basename(
            destination
        )

        db.commit()

        return {
            "message": "Document uploaded successfully",
            "document_id": new_document.id,
            "vehicle_id": vehicle_id,
            "category": category,
            "filename": new_document.file_name
        }

    finally:
        db.close()