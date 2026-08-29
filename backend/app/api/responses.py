from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.response import Response
from app.models.session import Session as SessionModel
from app.models.consent import Consent
from app.schemas.response import ResponseCreate, ResponseResponse


router = APIRouter(
    prefix="/responses",
    tags=["Responses"]
)


# Create Response
@router.post("/", response_model=ResponseResponse)
def create_response(
    response: ResponseCreate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == response.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Check capture consent
    consent = db.query(Consent).filter(
        Consent.session_id == response.session_id
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

    new_response = Response(
        session_id=response.session_id,
        question=response.question,
        answer=response.answer,
        input_type=response.input_type,
        language=response.language
    )

    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    return new_response


# Get All Responses
@router.get("/", response_model=list[ResponseResponse])
def get_responses(db: Session = Depends(get_db)):
    return db.query(Response).all()


# Get One Response
@router.get("/{response_id}", response_model=ResponseResponse)
def get_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    response = db.query(Response).filter(
        Response.id == response_id
    ).first()

    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Response not found"
        )

    return response


# Update Response
@router.put("/{response_id}", response_model=ResponseResponse)
def update_response(
    response_id: int,
    response_data: ResponseCreate,
    db: Session = Depends(get_db)
):
    response = db.query(Response).filter(
        Response.id == response_id
    ).first()

    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Response not found"
        )

    session = db.query(SessionModel).filter(
        SessionModel.id == response_data.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    response.session_id = response_data.session_id
    response.question = response_data.question
    response.answer = response_data.answer
    response.input_type = response_data.input_type
    response.language = response_data.language

    db.commit()
    db.refresh(response)

    return response


# Delete Response
@router.delete("/{response_id}")
def delete_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    response = db.query(Response).filter(
        Response.id == response_id
    ).first()

    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Response not found"
        )

    db.delete(response)
    db.commit()

    return {
        "message": "Response deleted successfully"
    }