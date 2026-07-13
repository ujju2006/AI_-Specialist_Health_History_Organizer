"""
Family Medical History Router
=============================
Provides CRUD endpoints for tracking family medical conditions across parents,
grandparents, siblings, and children, computing display-only genetic risk indicators.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import FamilyMedicalHistoryCreate, FamilyMedicalHistoryResponse
from app.routers.deps import get_current_active_user
from app.repositories.repositories import family_repo

router = APIRouter(prefix="/family", tags=["Family Medical History"])


@router.get("", response_model=List[FamilyMedicalHistoryResponse])
def list_family_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists all recorded family medical history items for the authenticated user.
    """
    return family_repo.get_user_family_history(db, current_user.id)


@router.post("", response_model=FamilyMedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
def add_family_history(
    item_in: FamilyMedicalHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Adds a new family medical condition record (e.g. Father - Hypertension).
    """
    data = item_in.model_dump()
    data["user_id"] = current_user.id
    return family_repo.create(db, data)


@router.delete("/{item_id}")
def delete_family_history(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Removes a family medical history item (using soft delete).
    """
    item = family_repo.get(db, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Family history item not found.")
    
    family_repo.delete(db, item_id)
    return {"status": "success", "deleted_id": item_id}
