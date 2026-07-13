"""
Health Goals Router
===================
Provides endpoints for creating, updating, and monitoring personalized health targets
with automatic progress calculations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import HealthGoalCreate, HealthGoalResponse, HealthGoalUpdate
from app.routers.deps import get_current_active_user
from app.repositories.repositories import goal_repo, vitals_repo

router = APIRouter(prefix="/goals", tags=["Health Goals & Targets"])


@router.get("", response_model=List[HealthGoalResponse])
def list_health_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists all active health goals and computes progress percentage against latest vitals.
    """
    goals = goal_repo.get_user_goals(db, current_user.id)
    vitals = vitals_repo.get_user_vitals(db, current_user.id)
    latest = vitals[0] if vitals else None

    for g in goals:
        if latest and g.status == "Active":
            if "Weight" in g.goal_type and latest.weight_kg:
                g.current_value = latest.weight_kg
            elif "Blood Sugar" in g.goal_type and latest.blood_sugar_mgdl:
                g.current_value = latest.blood_sugar_mgdl
            elif "Systolic" in g.goal_type and latest.systolic_bp:
                g.current_value = latest.systolic_bp
            elif "Diastolic" in g.goal_type and latest.diastolic_bp:
                g.current_value = latest.diastolic_bp

            if g.current_value is not None and g.target_value is not None and g.current_value > 0:
                # Basic progress estimate toward target
                diff = abs(g.current_value - g.target_value)
                pct = max(0.0, round(100.0 - (diff / g.target_value * 100.0), 1))
                g.progress_percent = min(100.0, pct)
            db.add(g)
    db.commit()
    return goals


@router.post("", response_model=HealthGoalResponse, status_code=status.HTTP_201_CREATED)
def create_health_goal(
    goal_in: HealthGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new health goal target.
    """
    data = goal_in.model_dump()
    data["user_id"] = current_user.id
    return goal_repo.create(db, data)


@router.put("/{goal_id}", response_model=HealthGoalResponse)
def update_health_goal(
    goal_id: str,
    goal_update: HealthGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates goal target, current value, or completion status.
    """
    goal_obj = goal_repo.get(db, goal_id)
    if not goal_obj or goal_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Health goal not found.")

    update_data = goal_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(goal_obj, k):
            setattr(goal_obj, k, v)
            
    if hasattr(goal_obj, "version"):
        goal_obj.version = (goal_obj.version or 1) + 1

    db.add(goal_obj)
    db.commit()
    db.refresh(goal_obj)
    return goal_obj


@router.delete("/{goal_id}")
def delete_health_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deletes a health goal (using soft delete).
    """
    goal_obj = goal_repo.get(db, goal_id)
    if not goal_obj or goal_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Health goal not found.")
    
    goal_repo.delete(db, goal_id)
    return {"status": "success", "deleted_id": goal_id}
