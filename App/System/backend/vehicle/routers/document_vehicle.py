# --------------------------------------------------
# documents.py
#
# Maintain Hub Document API
#
# Purpose:
# - List documents
# - Create document records
# - Download/view documents
# - Archive documents
#
# Notes:
# - Physical files are stored in the
#   YourDataFolder vehicle structure.
#
# - Database records store:
#     file_name
#     file_path
#     document_type
#     upload_date
#
# - Downloads are served using
#   FastAPI FileResponse.
#
# Future Enhancements:
# - Delete document endpoint
# - Restore archived document endpoint
# - Document search/filtering
# - Bulk document export
# --------------------------------------------------
import io
import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse

from PIL import Image

try:
    from pillow_heif import register_heif_opener
except ImportError:  # pragma: no cover
    register_heif_opener = None

from database import SessionLocal
from models import Document
from schemas.document import DocumentCreate

from helpers.storage import (
get_absolute_storage_path
)


router = APIRouter()


def _get_inline_document_response(document, full_path: str):
    """Return a file response that shows in-browser when possible."""
    filename = document.file_name or "document"
    extension = os.path.splitext(filename)[1].lower()

    if extension in [".heic", ".heif"]:
        if register_heif_opener is not None:
            register_heif_opener()

        image = Image.open(full_path)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        preview_buffer = io.BytesIO()
        image.save(preview_buffer, format="JPEG", quality=85, optimize=True)
        preview_buffer.seek(0)

        preview_name = os.path.splitext(filename)[0] + ".jpg"
        return StreamingResponse(
            preview_buffer,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'inline; filename="{preview_name}"'
            }
        )

    return FileResponse(
        path=full_path,
        filename=filename,
        content_disposition_type="inline"
    )


# --------------------------------------------------
# Get All Documents
# --------------------------------------------------

@router.get("/documents")
def get_documents():

    db = SessionLocal()

    documents = db.query(Document).filter(
        Document.domain == "Vehicle"
    ).all()

    results = []

    for document in documents:

        results.append({
            "id": document.id,
            "vehicle_id": document.vehicle_id,
            "document_type": document.document_type,
            "file_name": document.file_name,
            "file_path": document.file_path,
            "upload_date": document.upload_date
        })

    db.close()

    return results


# --------------------------------------------------
# Create Document Record
# --------------------------------------------------

@router.post("/documents")
def create_document(document: DocumentCreate):

    db = SessionLocal()

    new_document = Document(
        domain=document.domain or "Vehicle",
        vehicle_id=document.vehicle_id,

        maintenance_visit_id=
            document.maintenance_visit_id,

        document_type=document.document_type,
        file_name=document.file_name,
        file_path=document.file_path,
        upload_date=document.upload_date,
        notes=document.notes
    )

    db.add(new_document)

    db.commit()

    db.refresh(new_document)

    db.close()

    return {
        "message": "Document added",
        "id": new_document.id
    }


# --------------------------------------------------
# Download / View Document
# --------------------------------------------------

@router.get("/documents/{document_id}/preview")
def preview_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.domain == "Vehicle"
    ).first()

    db.close()

    if not document:
        return {
            "error": "Document not found"
        }

    stored_path = document.file_path

    if os.path.isabs(stored_path):
        full_path = stored_path
    else:
        full_path = get_absolute_storage_path(
            stored_path
        )

    return _get_inline_document_response(document, full_path)


@router.get("/documents/{document_id}/download")
def download_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.domain == "Vehicle"
    ).first()

    db.close()

    if not document:

        return {
            "error": "Document not found"
        }

    stored_path = document.file_path

    if os.path.isabs(stored_path):
        full_path = stored_path
    else:
        full_path = get_absolute_storage_path(
            stored_path
        )

    return FileResponse(
        path=full_path,
        filename=document.file_name,
        content_disposition_type="inline"
    )


# --------------------------------------------------
# Archive Document
# --------------------------------------------------

@router.post("/documents/{document_id}/archive")
def archive_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.domain == "Vehicle"
    ).first()

    if not document:

        db.close()

        return {
            "error": "Document not found"
        }

    document.archived = True

    db.commit()

    db.close()

    return {
        "message": "Document archived"
    }


# --------------------------------------------------
# Developer Notes
# --------------------------------------------------
#
# Expected download URL:
#
#   /documents/10/download
#
# If the browser is requesting:
#
#   /document/10
#
# instead of:
#
#   /documents/10/download
#
# then the issue is in the HTML template
# generating the View link, not in this file.
#
# Check:
#
#   templates/
#       documents.html
#       vehicle_documents.html
#
# and locate the View button hyperlink.
# --------------------------------------------------