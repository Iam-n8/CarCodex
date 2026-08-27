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

from fastapi import APIRouter
from fastapi.responses import FileResponse

from database import SessionLocal
from models import Document
from schemas.document import DocumentCreate

router = APIRouter()


# --------------------------------------------------
# Get All Documents
# --------------------------------------------------

@router.get("/documents")
def get_documents():

    db = SessionLocal()

    documents = db.query(Document).all()

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

@router.get("/documents/{document_id}/download")
def download_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    db.close()

    if not document:

        return {
            "error": "Document not found"
        }

    return FileResponse(
        path=document.file_path,
        filename=document.file_name
    )


# --------------------------------------------------
# Archive Document
# --------------------------------------------------

@router.post("/documents/{document_id}/archive")
def archive_document(document_id: int):

    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id
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