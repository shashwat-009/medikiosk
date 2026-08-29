from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.session import Session as SessionModel
from app.models.response import Response
from app.models.document import Document
from app.models.summary import Summary

from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.schemas.session import SessionResponse
from app.schemas.review import DoctorReviewResponse


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


# Create Doctor
@router.post("/", response_model=DoctorResponse)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db)
):
    new_doctor = Doctor(
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        department=doctor_data.department
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


# Get All Doctors
@router.get("/", response_model=list[DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


# Get One Doctor
@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# Update Doctor
@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    doctor.name = doctor_data.name
    doctor.specialization = doctor_data.specialization
    doctor.department = doctor_data.department

    db.commit()
    db.refresh(doctor)

    return doctor


# Delete Doctor
@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    db.delete(doctor)
    db.commit()

    return {
        "message": "Doctor deleted successfully"
    }


# Get Sessions Assigned to Doctor
@router.get(
    "/{doctor_id}/sessions",
    response_model=list[SessionResponse]
)
def get_doctor_sessions(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    sessions = db.query(SessionModel).filter(
        SessionModel.doctor_id == doctor_id
    ).all()

    return sessions


# Get Complete Session for Doctor Review
@router.get(
    "/{doctor_id}/sessions/{session_id}/review",
    response_model=DoctorReviewResponse
)
def get_session_for_review(
    doctor_id: int,
    session_id: int,
    db: Session = Depends(get_db)
):
    # Check doctor exists
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Check session exists and belongs to this doctor
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.doctor_id == doctor_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or not assigned to this doctor"
        )

    # Get patient
    patient = db.query(Patient).filter(
        Patient.id == session.patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Get responses
    responses = db.query(Response).filter(
        Response.session_id == session_id
    ).all()

    # Get documents
    documents = db.query(Document).filter(
        Document.session_id == session_id
    ).all()

    # Get summary
    summary = db.query(Summary).filter(
        Summary.session_id == session_id
    ).first()

    return {
        "session": session,
        "patient": patient,
        "responses": responses,
        "documents": documents,
        "summary": summary
    }