from pydantic import BaseModel

from app.schemas.session import SessionResponse
from app.schemas.patient import PatientResponse
from app.schemas.response import ResponseResponse
from app.schemas.document import DocumentResponse
from app.schemas.summary import SummaryResponse


class DoctorReviewResponse(BaseModel):
    session: SessionResponse
    patient: PatientResponse
    responses: list[ResponseResponse]
    documents: list[DocumentResponse]
    summary: SummaryResponse | None = None