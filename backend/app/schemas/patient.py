from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=150)
    gender: str
    phone: str | None = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    phone: str | None
    created_at: object

    class Config:
        from_attributes = True