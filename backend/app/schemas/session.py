from pydantic import BaseModel


class SessionCreate(BaseModel):
    patient_id: int


class SessionResponse(BaseModel):
    id: int
    patient_id: int
    status: str
    created_at: object

    class Config:
        from_attributes = True