"""
Consent & Data Sharing Router
=============================
Provides endpoints for generating temporary read-only access tokens,
managing active grants, and allowing external clinicians to view read-only health snapshots.
"""
from typing import List, Dict, Any
from datetime import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import ConsentShareTokenCreate, ConsentShareTokenResponse, MyHealthSnapshotResponse
from app.routers.deps import get_current_active_user
from app.repositories.repositories import consent_repo, user_repo, condition_repo, medication_repo, allergy_repo, contact_repo, vitals_repo
from app.analytics.analytics_engine import analytics_engine

router = APIRouter(prefix="/consent", tags=["Consent & Data Sharing"])


@router.post("/token", response_model=ConsentShareTokenResponse, status_code=status.HTTP_201_CREATED)
def generate_consent_token(
    token_in: ConsentShareTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generates a secure, temporary, read-only share token for clinical consultation.
    """
    token_str = secrets.token_urlsafe(24)
    data = {
        "user_id": current_user.id,
        "token_hash": token_str,
        "expires_at": token_in.expires_at,
        "permissions_scope": token_in.permissions_scope or "read_only_snapshot",
        "recipient_name": token_in.recipient_name or "External Healthcare Provider",
        "is_revoked": False
    }
    return consent_repo.create(db, data)


@router.get("/tokens", response_model=List[ConsentShareTokenResponse])
def list_active_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists all active, unrevoked consent share tokens for the user.
    """
    return consent_repo.get_user_tokens(db, current_user.id)


@router.delete("/token/{token_hash}")
def revoke_consent_token(
    token_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Immediately revokes access for a specific consent share token.
    """
    token_obj = consent_repo.get_by_token(db, token_hash)
    if not token_obj or token_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Token not found.")

    token_obj.is_revoked = True
    db.add(token_obj)
    db.commit()
    return {"status": "revoked", "token_hash": token_hash}


@router.get("/view/{token_hash}", response_model=MyHealthSnapshotResponse)
def view_shared_snapshot(
    token_hash: str,
    db: Session = Depends(get_db)
):
    """
    Public read-only endpoint for external doctors/consultants to view a patient's
    health snapshot using a valid consent share token.
    """
    token_obj = consent_repo.get_by_token(db, token_hash)
    if not token_obj or token_obj.is_revoked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent share token is invalid or revoked.")

    if token_obj.expires_at and datetime.utcnow() > token_obj.expires_at:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent share token has expired.")

    # Increment access count
    token_obj.access_count = (token_obj.access_count or 0) + 1
    token_obj.last_accessed_at = datetime.utcnow()
    db.add(token_obj)
    db.commit()

    patient = user_repo.get(db, token_obj.user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient account not found.")

    conditions = condition_repo.get_user_conditions(db, patient.id)
    meds = medication_repo.get_user_medications(db, patient.id)
    allergies = allergy_repo.get_user_allergies(db, patient.id)
    contacts = contact_repo.get_user_contacts(db, patient.id)
    vitals = vitals_repo.get_user_vitals(db, patient.id)

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
        user_id=patient.id,
        patient_name=f"{patient.first_name or ''} {patient.last_name or ''}".strip() or patient.email,
        blood_group=patient.blood_group or "Not specified",
        organ_donor_status=patient.organ_donor_status or "No",
        primary_care_physician=patient.primary_care_physician or "None on file",
        pcp_contact=patient.pcp_contact or "N/A",
        allergies=allergy_names,
        chronic_conditions=active_cond_names,
        active_medications_count=active_meds_count,
        emergency_contact=em_name,
        emergency_contact_phone=em_phone,
        latest_vitals=latest_vitals_dict,
        health_score=score_res["score"],
        health_score_label=score_res["label"]
    )
