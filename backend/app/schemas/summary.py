from pydantic import BaseModel


class SummaryCreate(BaseModel):
    session_id: int
    content: str


class SummaryUpdate(BaseModel):
    content: str | None = None
    status: str | None = None


class SummaryResponse(BaseModel):
    id: int
    session_id: int
    content: str
    status: str
    created_at: object
    updated_at: object

    class Config:
        from_attributes = True