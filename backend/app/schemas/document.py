from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    session_id: int | None
    filename: str
    document_type: str
    file_path: str
    created_at: object

    class Config:
        from_attributes = True