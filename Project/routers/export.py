"""
Data Export Router
==================
Provides standardized data export endpoints (FHIR-inspired JSON bundles and portable
clinical summaries) for interoperability and personal records backup.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.routers.deps import get_current_active_user
from app.repositories.repositories import (
    condition_repo, medication_repo, allergy_repo, vitals_repo,
    vaccination_repo, visit_repo, appointment_repo, contact_repo, family_repo
)
from app.services.export_service import export_service

router = APIRouter(prefix="/export", tags=["Data Interoperability & Export"])


@router.get("/fhir")
def export_fhir_bundle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Exports the authenticated user's complete health record as an HL7 FHIR-inspired JSON bundle.
    """
    conditions = condition_repo.get_user_conditions(db, current_user.id)
    medications = medication_repo.get_user_medications(db, current_user.id)
    allergies = allergy_repo.get_user_allergies(db, current_user.id)
    vitals = vitals_repo.get_user_vitals(db, current_user.id)
    vaccinations = vaccination_repo.get_user_vaccinations(db, current_user.id)
    visits = visit_repo.get_user_visits(db, current_user.id)
    appointments = appointment_repo.get_user_appointments(db, current_user.id)
    contacts = contact_repo.get_user_contacts(db, current_user.id)
    family = family_repo.get_user_family_history(db, current_user.id)

    return export_service.generate_fhir_inspired_bundle(
        user=current_user,
        conditions=conditions,
        medications=medications,
        allergies=allergies,
        vitals=vitals,
        vaccinations=vaccinations,
        visits=visits,
        appointments=appointments,
        contacts=contacts,
        family_histories=family
    )


@router.get("/summary")
def export_portable_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Exports a clean, structured clinical summary suitable for printing or PDF rendering.
    """
    conditions = condition_repo.get_user_conditions(db, current_user.id)
    medications = medication_repo.get_user_medications(db, current_user.id)
    allergies = allergy_repo.get_user_allergies(db, current_user.id)
    vitals = vitals_repo.get_user_vitals(db, current_user.id)
    contacts = contact_repo.get_user_contacts(db, current_user.id)

    return export_service.generate_portable_summary(
        user=current_user,
        conditions=conditions,
        medications=medications,
        allergies=allergies,
        vitals=vitals,
        contacts=contacts
    )
