from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.session import Session as SessionModel
from app.models.consent import Consent
from app.schemas.consent import ConsentCreate, ConsentResponse


router = APIRouter(
    prefix="/consents",
    tags=["Consents"]
)


# Create Consent
@router.post("/", response_model=ConsentResponse)
def create_consent(
    consent_data: ConsentCreate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == consent_data.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    existing_consent = db.query(Consent).filter(
        Consent.session_id == consent_data.session_id
    ).first()

    if existing_consent is not None:
        raise HTTPException(
            status_code=400,
            detail="Consent already exists for this session"
        )

    new_consent = Consent(
        session_id=consent_data.session_id,
        capture_consent=consent_data.capture_consent,
        sharing_consent=consent_data.sharing_consent,
        language=consent_data.language
    )

    db.add(new_consent)
    db.commit()
    db.refresh(new_consent)

    return new_consent


# Get Consent for a Session
@router.get(
    "/session/{session_id}",
    response_model=ConsentResponse
)
def get_session_consent(
    session_id: int,
    db: Session = Depends(get_db)
):
    consent = db.query(Consent).filter(
        Consent.session_id == session_id
    ).first()

    if consent is None:
        raise HTTPException(
            status_code=404,
            detail="Consent not found"
        )

    return consent