from pydantic import BaseModel


class DoctorCreate(BaseModel):
    name: str
    specialization: str | None = None
    department: str | None = None


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str | None
    department: str | None
    created_at: object

    class Config:
        from_attributes = True