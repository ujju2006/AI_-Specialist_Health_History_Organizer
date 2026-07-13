from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.deps import get_current_user
from app.models.models import User
from app.services.health_service import health_service
from app.services.insights_service import insights_service
from app.services.analytics_engine import analytics_engine
from app.services.notification_engine import notification_engine
from app.schemas.schemas import (
    MedicalConditionCreate, MedicalConditionUpdate, MedicalConditionResponse,
    MedicationCreate, MedicationUpdate, MedicationResponse,
    AllergyCreate, AllergyUpdate, AllergyResponse,
    DoctorVisitCreate, DoctorVisitUpdate, DoctorVisitResponse,
    VaccinationCreate, VaccinationUpdate, VaccinationResponse,
    VitalsCreate, VitalsResponse,
    AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    EmergencyContactCreate, EmergencyContactUpdate, EmergencyContactResponse,
    MedicalDocumentResponse, GlobalSearchResults
)

router = APIRouter(tags=["Health Framework"])

# --- Medical Conditions ---
@router.post("/conditions", response_model=MedicalConditionResponse, status_code=status.HTTP_201_CREATED)
def create_condition(data: MedicalConditionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_condition(db, user.id, data)

@router.get("/conditions", response_model=List[MedicalConditionResponse])
def get_conditions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_conditions(db, user.id)

@router.put("/conditions/{id}", response_model=MedicalConditionResponse)
def update_condition(id: str, data: MedicalConditionUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_condition(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/conditions/{id}", response_model=MedicalConditionResponse)
def delete_condition(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_condition(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Medications ---
@router.post("/medications", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(data: MedicationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_medication(db, user.id, data)

@router.get("/medications", response_model=List[MedicationResponse])
def get_medications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_medications(db, user.id)

@router.put("/medications/{id}", response_model=MedicationResponse)
def update_medication(id: str, data: MedicationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_medication(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/medications/{id}", response_model=MedicationResponse)
def delete_medication(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_medication(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Allergies ---
@router.post("/allergies", response_model=AllergyResponse, status_code=status.HTTP_201_CREATED)
def create_allergy(data: AllergyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_allergy(db, user.id, data)

@router.get("/allergies", response_model=List[AllergyResponse])
def get_allergies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_allergies(db, user.id)

@router.put("/allergies/{id}", response_model=AllergyResponse)
def update_allergy(id: str, data: AllergyUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_allergy(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/allergies/{id}", response_model=AllergyResponse)
def delete_allergy(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_allergy(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Doctor Visits ---
@router.post("/visits", response_model=DoctorVisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(data: DoctorVisitCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_visit(db, user.id, data)

@router.get("/visits", response_model=List[DoctorVisitResponse])
def get_visits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_visits(db, user.id)

@router.put("/visits/{id}", response_model=DoctorVisitResponse)
def update_visit(id: str, data: DoctorVisitUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_visit(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/visits/{id}", response_model=DoctorVisitResponse)
def delete_visit(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_visit(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Vaccinations ---
@router.post("/vaccinations", response_model=VaccinationResponse, status_code=status.HTTP_201_CREATED)
def create_vaccination(data: VaccinationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_vaccination(db, user.id, data)

@router.get("/vaccinations", response_model=List[VaccinationResponse])
def get_vaccinations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_vaccinations(db, user.id)

@router.put("/vaccinations/{id}", response_model=VaccinationResponse)
def update_vaccination(id: str, data: VaccinationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_vaccination(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/vaccinations/{id}", response_model=VaccinationResponse)
def delete_vaccination(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_vaccination(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Vitals Measurements ---
@router.post("/vitals", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
def create_vitals(data: VitalsCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_vitals(db, user.id, data)

@router.get("/vitals", response_model=List[VitalsResponse])
def get_vitals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_vitals(db, user.id)

@router.delete("/vitals/{id}", response_model=VitalsResponse)
def delete_vitals(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_vitals(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Appointments ---
@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_appointment(db, user.id, data)

@router.get("/appointments", response_model=List[AppointmentResponse])
def get_appointments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_appointments(db, user.id)

@router.put("/appointments/{id}", response_model=AppointmentResponse)
def update_appointment(id: str, data: AppointmentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_appointment(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/appointments/{id}", response_model=AppointmentResponse)
def delete_appointment(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_appointment(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Emergency Contacts ---
@router.post("/emergency", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(data: EmergencyContactCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.create_contact(db, user.id, data)

@router.get("/emergency", response_model=List[EmergencyContactResponse])
def get_contacts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_contacts(db, user.id)

@router.put("/emergency/{id}", response_model=EmergencyContactResponse)
def update_contact(id: str, data: EmergencyContactUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.update_contact(db, user.id, id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/emergency/{id}", response_model=EmergencyContactResponse)
def delete_contact(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_contact(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Documents Management ---
@router.post("/documents", response_model=MedicalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        return health_service.save_document(
            db=db,
            user_id=user.id,
            title=title,
            description=description,
            filename=file.filename,
            content=content,
            mime_type=file.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/documents", response_model=List[MedicalDocumentResponse])
def get_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return health_service.get_documents(db, user.id)

@router.delete("/documents/{id}", response_model=MedicalDocumentResponse)
def delete_document(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return health_service.delete_document(db, user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/documents/{id}/download")
def download_document(id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch document from db
    from app.repositories.repositories import document_repo
    doc = document_repo.get(db, id)
    if not doc or doc.user_id != user.id:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path=doc.file_path, filename=doc.title, media_type=doc.mime_type)


# --- Analytics Dashboard (Analytics Engine → Insight Generator pipeline) ---
@router.get("/analytics/summary")
def get_analytics_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Health analytics summary.
    Pipeline: Core Services → Analytics Engine → Insight Generator → Dashboard
    The Analytics Engine handles all computation; the Insight Generator produces
    educational narrative text. The two layers are intentionally separated.
    """
    # 1. Fetch raw data via core services
    user_vitals = health_service.get_vitals(db, user.id)
    user_meds = health_service.get_medications(db, user.id)
    user_vaccines = health_service.get_vaccinations(db, user.id)
    user_visits = health_service.get_visits(db, user.id)
    user_appointments = health_service.get_appointments(db, user.id)

    # 2. Analytics Engine: trend detection, scoring, risk classification
    health_score = analytics_engine.calculate_health_score(user_vitals)
    health_score_label = analytics_engine.classify_health_score(health_score)
    bp_analytics = analytics_engine.get_bp_analytics(user_vitals)
    weight_analytics = analytics_engine.get_weight_analytics(user_vitals)
    sugar_analytics = analytics_engine.get_sugar_analytics(user_vitals)
    pulse_analytics = analytics_engine.get_pulse_analytics(user_vitals)
    oxygen_analytics = analytics_engine.get_oxygen_analytics(user_vitals)
    temperature_analytics = analytics_engine.get_temperature_analytics(user_vitals)
    medication_analytics = analytics_engine.get_medication_adherence(user_meds)
    vaccination_analytics = analytics_engine.get_vaccination_summary(user_vaccines)
    visit_analytics = analytics_engine.get_visit_summary(user_visits)
    appointment_timeline = analytics_engine.get_appointment_timeline(user_appointments)
    weekly_summary = analytics_engine.get_weekly_summary(user_vitals)

    # 3. Insight Generator (AI layer): educational narrative only
    ai_insights = insights_service.generate_ai_insights(
        vitals=user_vitals,
        medications=user_meds,
        bp_analytics=bp_analytics,
        weight_analytics=weight_analytics,
        sugar_analytics=sugar_analytics,
    )

    return {
        "health_score": health_score,
        "health_score_label": health_score_label,
        "weekly_summary": weekly_summary,
        "blood_pressure": bp_analytics,
        "weight_bmi": weight_analytics,
        "blood_sugar": sugar_analytics,
        "pulse": pulse_analytics,
        "oxygen": oxygen_analytics,
        "temperature": temperature_analytics,
        "medications": medication_analytics,
        "vaccinations": vaccination_analytics,
        "visits": visit_analytics,
        "appointment_timeline": appointment_timeline,
        "ai_insights": ai_insights,
    }


# --- Notification Engine ---
@router.get("/notifications")
def get_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns prioritised in-app notifications:
    - Upcoming appointments (within 7 days)
    - Due / overdue vaccinations
    - Low medication adherence alerts
    - Annual health check reminder
    """
    user_appointments = health_service.get_appointments(db, user.id)
    user_vaccines = health_service.get_vaccinations(db, user.id)
    user_meds = health_service.get_medications(db, user.id)
    user_visits = health_service.get_visits(db, user.id)

    return notification_engine.get_all_notifications(
        appointments=user_appointments,
        vaccinations=user_vaccines,
        medications=user_meds,
        visits=user_visits,
    )


# --- Security: Audit Log Dashboard ---
@router.get("/audit/logs")
def get_audit_logs(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the current user's immutable audit trail.
    Shows: who did what, to which record, from which device, at what time.
    Useful for the security event dashboard (recent logins, data changes).
    """
    from app.repositories.repositories import audit_repo
    logs = audit_repo.get_user_logs(db, user.id, limit=min(limit, 200))
    return [
        {
            "id": log.id,
            "correlation_id": log.correlation_id,
            "event_type": log.event_type,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "endpoint": log.endpoint,
            "http_method": log.http_method,
            "ip_address": log.ip_address,
            "browser": log.browser,
            "device_type": log.device_type,
            "status_code": log.status_code,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]


# --- Global Search Route ---
@router.get("/search", response_model=GlobalSearchResults)
def global_search(query: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Performs global case-insensitive search queries on user medical history models.
    """
    from sqlalchemy import or_
    from app.models.models import MedicalCondition, Medication, Vitals, Appointment

    q_lower = f"%{query.lower()}%"

    conditions = db.query(MedicalCondition).filter(
        MedicalCondition.user_id == user.id,
        or_(
            MedicalCondition.name.ilike(q_lower),
            MedicalCondition.notes.ilike(q_lower)
        )
    ).all()

    medications = db.query(Medication).filter(
        Medication.user_id == user.id,
        or_(
            Medication.name.ilike(q_lower),
            Medication.dosage.ilike(q_lower),
            Medication.frequency.ilike(q_lower)
        )
    ).all()

    # Vitals match - can matching string indicators like high BP or specific symptoms in logs
    # In vitals, we can fetch all and return matching subset
    vitals = db.query(Vitals).filter(
         Vitals.user_id == user.id
    ).all() # Just return user's vitals for display or empty

    appointments = db.query(Appointment).filter(
        Appointment.user_id == user.id,
        or_(
            Appointment.doctor_name.ilike(q_lower),
            Appointment.specialty.ilike(q_lower),
            Appointment.location.ilike(q_lower)
        )
    ).all()

    return {
        "conditions": conditions,
        "medications": medications,
        "vitals": vitals[:5] if query == "" else [], 
        "appointments": appointments
    }
