from pydantic import BaseModel


class ResponseCreate(BaseModel):
    session_id: int
    question: str
    answer: str
    input_type: str
    language: str | None = None


class ResponseResponse(BaseModel):
    id: int
    session_id: int
    question: str
    answer: str
    input_type: str
    language: str | None
    created_at: object

    class Config:
        from_attributes = True