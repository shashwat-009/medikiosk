from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.session import Session as SessionModel
from app.models.summary import Summary
from app.schemas.summary import (
    SummaryCreate,
    SummaryResponse,
    SummaryUpdate,
)


router = APIRouter(
    prefix="/summaries",
    tags=["Summaries"]
)


@router.post("/", response_model=SummaryResponse)
def create_summary(
    summary_data: SummaryCreate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == summary_data.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    new_summary = Summary(
        session_id=summary_data.session_id,
        content=summary_data.content
    )

    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return new_summary


@router.get("/", response_model=list[SummaryResponse])
def get_summaries(db: Session = Depends(get_db)):
    return db.query(Summary).all()


@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    summary = db.query(Summary).filter(
        Summary.id == summary_id
    ).first()

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Summary not found"
        )

    return summary


@router.put("/{summary_id}", response_model=SummaryResponse)
def update_summary(
    summary_id: int,
    summary_data: SummaryUpdate,
    db: Session = Depends(get_db)
):
    summary = db.query(Summary).filter(
        Summary.id == summary_id
    ).first()

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Summary not found"
        )

    if summary_data.content is not None:
        summary.content = summary_data.content

    if summary_data.status is not None:
        if summary_data.status not in [
            "draft",
            "accepted",
            "rejected"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Invalid summary status"
            )

        summary.status = summary_data.status

    db.commit()
    db.refresh(summary)

    return summary


@router.delete("/{summary_id}")
def delete_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    summary = db.query(Summary).filter(
        Summary.id == summary_id
    ).first()

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Summary not found"
        )

    db.delete(summary)
    db.commit()

    return {
        "message": "Summary deleted successfully"
    }