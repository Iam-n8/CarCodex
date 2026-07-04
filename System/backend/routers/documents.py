from fastapi import APIRouter
from pydantic import BaseModel

from database import SessionLocal
from models import Document

router = APIRouter()


class DocumentCreate(BaseModel):
    vehicle_id: int
    document_type: str
    file_name: str
    file_path: str
    upload_date: str
    notes: str


@router.get("/documents")
def get_documents():

    db = SessionLocal()

    documents = db.query(Document).all()

    results = []

    for document in documents:
        results.append({
            "id": document.id,
            "file_name": document.file_name
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
