from fastapi import FastAPI

from app.config import settings
from app.db.database import Base, engine
from app.models.patient import Patient
from app.models.session import Session
from app.models.document import Document
from app.models.response import Response
from app.models.summary import Summary
from app.api.patients import router as patients_router
from app.api.sessions import router as sessions_router
from app.api.documents import router as documents_router
from app.api.responses import router as responses_router
from app.api.summary import router as summary_router



Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.include_router(patients_router)
app.include_router(sessions_router)
app.include_router(documents_router)
app.include_router(responses_router)
app.include_router(summary_router)


@app.get("/")
def root():
    return {
        "message": "MediKiosk API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }