import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.patient import Patient
from app.models.session import Session as SessionModel
from app.models.consent import Consent
from app.schemas.document import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# Upload Document
@router.post("/", response_model=DocumentResponse)
def upload_document(
    patient_id: int = Form(...),
    session_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check patient
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Check session
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Check session belongs to patient
    if session.patient_id != patient_id:
        raise HTTPException(
            status_code=400,
            detail="Session does not belong to this patient"
        )

    # Check capture consent
    consent = db.query(Consent).filter(
        Consent.session_id == session_id
    ).first()

    if consent is None:
        raise HTTPException(
            status_code=403,
            detail="Consent not found for this session"
        )

    if not consent.capture_consent or consent.revoked:
        raise HTTPException(
            status_code=403,
            detail="Valid capture consent is required"
        )

    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    stored_filename = f"{uuid4()}{file_extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create database record
    new_document = Document(
        patient_id=patient_id,
        session_id=session_id,
        filename=file.filename,
        document_type=document_type,
        file_path=file_path
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


# Get All Documents
@router.get("/", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()


# Get One Document
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# Delete Document
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete database record
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }