# document.py

from pydantic import BaseModel

class DocumentCreate(BaseModel):
    vehicle_id: int

    maintenance_visit_id: int | None = None

    document_type: str
    file_name: str
    file_path: str
    upload_date: str
    notes: str