from pydantic import BaseModel


class ConsentCreate(BaseModel):
    session_id: int
    capture_consent: bool
    sharing_consent: bool
    language: str | None = None


class ConsentResponse(BaseModel):
    id: int
    session_id: int
    capture_consent: bool
    sharing_consent: bool
    language: str | None
    created_at: object

    class Config:
        from_attributes = True