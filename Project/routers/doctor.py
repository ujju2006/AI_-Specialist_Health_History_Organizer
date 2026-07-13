"""
Doctor Clinical Portal Router
=============================
Provides endpoints for physicians and clinical staff to manage consultations,
view patient health records, update appointment lifecycles, and issue prescriptions.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, Appointment, Medication, MedicalCondition, Allergy, Vitals, Vaccination, DoctorVisit
from app.schemas.schemas import UserResponse, AppointmentResponse, MedicationCreate, MedicationResponse, AppointmentUpdate
from app.routers.deps import get_current_doctor
from app.repositories.repositories import (
    user_repo, appointment_repo, medication_repo, condition_repo, allergy_repo,
    vitals_repo, vaccination_repo, visit_repo
)
from app.analytics.analytics_engine import analytics_engine

router = APIRouter(prefix="/doctor", tags=["Doctor Clinical Portal"])


@router.get("/patients", response_model=List[UserResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    """
    Lists all patients in the platform for clinical review.
    """
    query = db.query(User).filter(User.is_deleted == False)
    if search:
        s = f"%{search.lower()}%"
        query = query.filter((User.email.ilike(s)) | (User.first_name.ilike(s)) | (User.last_name.ilike(s)))
    
    users = query.offset(skip).limit(limit).all()
    # Filter only users whose primary_role is Patient or just return all users for clinical visibility
    return users


@router.get("/patient/{patient_id}/records")
def get_patient_clinical_record(
    patient_id: str,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    """
    Retrieves the complete clinical record and analytics summary for a specific patient.
    """
    patient = user_repo.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found.")

    vitals = vitals_repo.get_user_vitals(db, patient_id)
    meds = medication_repo.get_user_medications(db, patient_id)
    conditions = condition_repo.get_user_conditions(db, patient_id)
    allergies = allergy_repo.get_user_allergies(db, patient_id)
    vaccinations = vaccination_repo.get_user_vaccinations(db, patient_id)
    visits = visit_repo.get_user_visits(db, patient_id)
    appointments = appointment_repo.get_user_appointments(db, patient_id)

    analytics = analytics_engine.get_comprehensive_analytics(
        vitals=vitals,
        medications=meds,
        vaccinations=vaccinations,
        visits=visits,
        appointments=appointments
    )

    return {
        "patient": {
            "id": patient.id,
            "email": patient.email,
            "name": f"{patient.first_name or ''} {patient.last_name or ''}".strip() or patient.email,
            "date_of_birth": patient.date_of_birth or "N/A",
            "gender": patient.gender or "N/A",
            "blood_group": patient.blood_group or "Unknown",
            "insurance_provider": patient.insurance_provider or "None",
            "primary_care_physician": patient.primary_care_physician or "None"
        },
        "conditions": [{"id": c.id, "name": c.name, "status": c.status, "diagnosed": c.diagnosed_date, "notes": c.notes} for c in conditions],
        "allergies": [{"id": a.id, "allergen": a.allergen, "severity": a.severity, "reaction": a.reaction} for a in allergies],
        "medications": [{"id": m.id, "name": m.name, "dosage": m.dosage, "frequency": m.frequency, "status": m.status, "adherence_rate": m.adherence_rate} for m in meds],
        "vitals_count": len(vitals),
        "analytics_summary": analytics
    }


@router.get("/appointments", response_model=List[AppointmentResponse])
def list_doctor_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    """
    Lists upcoming consultations and appointments across all patients.
    """
    return db.query(Appointment).filter(Appointment.is_deleted == False).order_by(Appointment.appointment_date).offset(skip).limit(limit).all()


@router.put("/appointment/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_lifecycle(
    appointment_id: str,
    status_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    """
    Updates appointment status through clinical lifecycle:
    Requested -> Confirmed -> Checked In -> Consultation -> Prescription Issued -> Completed
    """
    app_obj = appointment_repo.get(db, appointment_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if status_update.status:
        app_obj.status = status_update.status
    if status_update.notes:
        app_obj.notes = status_update.notes
    if hasattr(app_obj, "version"):
        app_obj.version = (app_obj.version or 1) + 1

    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj


@router.post("/patient/{patient_id}/prescription", response_model=MedicationResponse)
def issue_prescription(
    patient_id: str,
    medication_in: MedicationCreate,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    """
    Issues a new prescription medication record directly to a patient's health vault.
    """
    patient = user_repo.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    med_data = medication_in.model_dump()
    med_data["user_id"] = patient_id
    med = medication_repo.create(db, med_data)
    return med
