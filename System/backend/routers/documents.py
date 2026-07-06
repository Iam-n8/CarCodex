from fastapi import APIRouter
from fastapi.responses import FileResponse
from schemas.document import DocumentCreate

from database import SessionLocal
from models import Document

router = APIRouter()

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


@router.post("/documents")
def create_document(document: DocumentCreate):

    db = SessionLocal()

    new_document = Document(
        vehicle_id=document.vehicle_id,
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