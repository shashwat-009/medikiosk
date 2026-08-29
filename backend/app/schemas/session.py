from pydantic import BaseModel


class SessionCreate(BaseModel):
    patient_id: int
    doctor_id: int | None = None


class SessionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int | None
    status: str
    created_at: object

    class Config:
        from_attributes = True