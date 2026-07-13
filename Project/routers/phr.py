"""
Personal Health Record (PHR) Router
===================================
Provides endpoints for managing comprehensive personal health profiles, insurance info,
emergency contacts, and generating the unified 'My Health Snapshot' card.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import MyHealthSnapshotResponse, UserUpdate, UserResponse
from app.routers.deps import get_current_active_user
from app.repositories.repositories import condition_repo, medication_repo, allergy_repo, contact_repo, vitals_repo
from app.analytics.analytics_engine import analytics_engine

router = APIRouter(prefix="/phr", tags=["Personal Health Record (PHR)"])


@router.get("/snapshot", response_model=MyHealthSnapshotResponse)
def get_my_health_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns the unified 'My Health Snapshot' combining blood group, organ donor status,
    PCP contact, allergies, chronic conditions, active medications count, emergency contacts, and latest vitals.
    """
    conditions = condition_repo.get_user_conditions(db, current_user.id)
    meds = medication_repo.get_user_medications(db, current_user.id)
    allergies = allergy_repo.get_user_allergies(db, current_user.id)
    contacts = contact_repo.get_user_contacts(db, current_user.id)
    vitals = vitals_repo.get_user_vitals(db, current_user.id)

    active_cond_names = [c.name for c in conditions if c.status == "Active"]
    allergy_names = [f"{a.allergen} ({a.severity})" for a in allergies]
    active_meds_count = sum(1 for m in meds if m.status == "Active")

    em_name = "None on file"
    em_phone = "N/A"
    if contacts:
        em_name = f"{contacts[0].name} ({contacts[0].relationship})"
        em_phone = contacts[0].phone_number

    latest_vitals_dict = None
    if vitals:
        v = vitals[0]
        latest_vitals_dict = {
            "systolic_bp": v.systolic_bp,
            "diastolic_bp": v.diastolic_bp,
            "weight_kg": v.weight_kg,
            "blood_sugar_mgdl": v.blood_sugar_mgdl,
            "pulse_bpm": v.pulse_bpm,
            "recorded_at": v.recorded_at.isoformat() if v.recorded_at else "N/A"
        }

    score_res = analytics_engine.get_detailed_health_score(vitals, meds)

    return MyHealthSnapshotResponse(
        user_id=current_user.id,
        patient_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        blood_group=current_user.blood_group or "Not specified",
        organ_donor_status=current_user.organ_donor_status or "No",
        primary_care_physician=current_user.primary_care_physician or "None on file",
        pcp_contact=current_user.pcp_contact or "N/A",
        allergies=allergy_names,
        chronic_conditions=active_cond_names,
        active_medications_count=active_meds_count,
        emergency_contact=em_name,
        emergency_contact_phone=em_phone,
        latest_vitals=latest_vitals_dict,
        health_score=score_res["score"],
        health_score_label=score_res["label"]
    )


@router.get("/profile", response_model=UserResponse)
def get_phr_profile(current_user: User = Depends(get_current_active_user)):
    """
    Retrieves full personal health record profile attributes.
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_phr_profile(
    profile_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates PHR attributes (insurance, PCP, blood group, organ donor status, lifestyle habits).
    """
    update_data = profile_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(current_user, k):
            setattr(current_user, k, v)
    
    if hasattr(current_user, "version"):
        current_user.version = (current_user.version or 1) + 1

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
