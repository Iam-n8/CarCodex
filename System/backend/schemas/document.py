from pydantic import BaseModel

class DocumentCreate(BaseModel):
    vehicle_id: int
    document_type: str
    file_name: str
    file_path: str
    upload_date: str
    notes: str