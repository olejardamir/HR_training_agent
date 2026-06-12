from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TrainingContent, OnboardingContent

router = APIRouter(prefix="/mock/content", tags=["content"])


@router.get("/training")
def get_training_content(
    module_id: str = Query(None, description="Filter by module ID (T1-T4)"),
    db: Session = Depends(get_db),
):
    query = db.query(TrainingContent)
    if module_id:
        query = query.filter(TrainingContent.module_ids.contains(module_id))
    items = query.all()
    return items


@router.get("/training/{content_id}")
def get_training_content_by_id(content_id: str, db: Session = Depends(get_db)):
    item = db.query(TrainingContent).filter(TrainingContent.content_id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Training content not found")
    return item


@router.get("/onboarding")
def get_onboarding_content(
    phase: str = Query(None, description="Filter by onboarding phase"),
    db: Session = Depends(get_db),
):
    query = db.query(OnboardingContent)
    if phase:
        query = query.filter(OnboardingContent.phases.contains(phase))
    items = query.all()
    return items


@router.get("/onboarding/{content_id}")
def get_onboarding_content_by_id(content_id: str, db: Session = Depends(get_db)):
    item = db.query(OnboardingContent).filter(OnboardingContent.content_id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Onboarding content not found")
    return item
