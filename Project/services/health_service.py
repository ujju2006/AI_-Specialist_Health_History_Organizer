import os
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.repositories import (
    condition_repo, medication_repo, allergy_repo,
    visit_repo, vaccination_repo, vitals_repo,
    appointment_repo, contact_repo, document_repo
)
from app.models.models import (
    MedicalCondition, Medication, Allergy, DoctorVisit,
    Vaccination, Vitals, Appointment, EmergencyContact, MedicalDocument
)
from app.schemas.schemas import (
    MedicalConditionCreate, MedicalConditionUpdate,
    MedicationCreate, MedicationUpdate,
    AllergyCreate, AllergyUpdate,
    DoctorVisitCreate, DoctorVisitUpdate,
    VaccinationCreate, VaccinationUpdate,
    VitalsCreate,
    AppointmentCreate, AppointmentUpdate,
    EmergencyContactCreate, EmergencyContactUpdate
)
from app.core.config import settings

class HealthService:
    # --- Conditions CRUD ---
    def create_condition(self, db: Session, user_id: str, data: MedicalConditionCreate) -> MedicalCondition:
        record = data.model_dump()
        record["user_id"] = user_id
        return condition_repo.create(db, record)

    def get_conditions(self, db: Session, user_id: str) -> List[MedicalCondition]:
        return condition_repo.filter(db, user_id=user_id)

    def update_condition(self, db: Session, user_id: str, id: str, data: MedicalConditionUpdate) -> MedicalCondition:
        obj = condition_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return condition_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_condition(self, db: Session, user_id: str, id: str) -> MedicalCondition:
        obj = condition_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return condition_repo.remove(db, id)

    # --- Medications CRUD ---
    def create_medication(self, db: Session, user_id: str, data: MedicationCreate) -> Medication:
        record = data.model_dump()
        record["user_id"] = user_id
        return medication_repo.create(db, record)

    def get_medications(self, db: Session, user_id: str) -> List[Medication]:
        return medication_repo.filter(db, user_id=user_id)

    def update_medication(self, db: Session, user_id: str, id: str, data: MedicationUpdate) -> Medication:
        obj = medication_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return medication_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_medication(self, db: Session, user_id: str, id: str) -> Medication:
        obj = medication_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return medication_repo.remove(db, id)

    # --- Allergies CRUD ---
    def create_allergy(self, db: Session, user_id: str, data: AllergyCreate) -> Allergy:
        record = data.model_dump()
        record["user_id"] = user_id
        return allergy_repo.create(db, record)

    def get_allergies(self, db: Session, user_id: str) -> List[Allergy]:
        return allergy_repo.filter(db, user_id=user_id)

    def update_allergy(self, db: Session, user_id: str, id: str, data: AllergyUpdate) -> Allergy:
        obj = allergy_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return allergy_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_allergy(self, db: Session, user_id: str, id: str) -> Allergy:
        obj = allergy_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return allergy_repo.remove(db, id)

    # --- Doctor Visits CRUD ---
    def create_visit(self, db: Session, user_id: str, data: DoctorVisitCreate) -> DoctorVisit:
        record = data.model_dump()
        record["user_id"] = user_id
        return visit_repo.create(db, record)

    def get_visits(self, db: Session, user_id: str) -> List[DoctorVisit]:
        return visit_repo.get_user_visits(db, user_id)

    def update_visit(self, db: Session, user_id: str, id: str, data: DoctorVisitUpdate) -> DoctorVisit:
        obj = visit_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return visit_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_visit(self, db: Session, user_id: str, id: str) -> DoctorVisit:
        obj = visit_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return visit_repo.remove(db, id)

    # --- Vaccinations CRUD ---
    def create_vaccination(self, db: Session, user_id: str, data: VaccinationCreate) -> Vaccination:
        record = data.model_dump()
        record["user_id"] = user_id
        return vaccination_repo.create(db, record)

    def get_vaccinations(self, db: Session, user_id: str) -> List[Vaccination]:
        return vaccination_repo.filter(db, user_id=user_id)

    def update_vaccination(self, db: Session, user_id: str, id: str, data: VaccinationUpdate) -> Vaccination:
        obj = vaccination_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return vaccination_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_vaccination(self, db: Session, user_id: str, id: str) -> Vaccination:
        obj = vaccination_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return vaccination_repo.remove(db, id)

    # --- Vitals CRUD ---
    def create_vitals(self, db: Session, user_id: str, data: VitalsCreate) -> Vitals:
        record = data.model_dump()
        record["user_id"] = user_id
        record["recorded_at"] = datetime.utcnow()
        return vitals_repo.create(db, record)

    def get_vitals(self, db: Session, user_id: str) -> List[Vitals]:
        return vitals_repo.get_user_vitals(db, user_id)

    def delete_vitals(self, db: Session, user_id: str, id: str) -> Vitals:
        obj = vitals_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return vitals_repo.remove(db, id)

    # --- Appointments CRUD ---
    def create_appointment(self, db: Session, user_id: str, data: AppointmentCreate) -> Appointment:
        record = data.model_dump()
        record["user_id"] = user_id
        return appointment_repo.create(db, record)

    def get_appointments(self, db: Session, user_id: str) -> List[Appointment]:
        return appointment_repo.get_user_appointments(db, user_id)

    def update_appointment(self, db: Session, user_id: str, id: str, data: AppointmentUpdate) -> Appointment:
        obj = appointment_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return appointment_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_appointment(self, db: Session, user_id: str, id: str) -> Appointment:
        obj = appointment_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return appointment_repo.remove(db, id)

    # --- Emergency Contacts CRUD ---
    def create_contact(self, db: Session, user_id: str, data: EmergencyContactCreate) -> EmergencyContact:
        record = data.model_dump()
        record["user_id"] = user_id
        return contact_repo.create(db, record)

    def get_contacts(self, db: Session, user_id: str) -> List[EmergencyContact]:
        return contact_repo.filter(db, user_id=user_id)

    def update_contact(self, db: Session, user_id: str, id: str, data: EmergencyContactUpdate) -> EmergencyContact:
        obj = contact_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return contact_repo.update(db, obj, data.model_dump(exclude_unset=True))

    def delete_contact(self, db: Session, user_id: str, id: str) -> EmergencyContact:
        obj = contact_repo.get(db, id)
        if not obj or obj.user_id != user_id:
            raise ValueError("Record not found")
        return contact_repo.remove(db, id)

    # --- Documents Management ---
    def save_document(self, db: Session, user_id: str, title: str, description: str, filename: str, content: bytes, mime_type: str) -> MedicalDocument:
        # File checks
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unacceptable file extension. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}")

        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB")

        # Save actual file to filesystem
        storage_filename = f"{user_id}_{int(datetime.utcnow().timestamp())}_{filename}"
        file_path = settings.UPLOAD_DIR / storage_filename
        
        with open(file_path, "wb") as f:
            f.write(content)

        document_details = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "file_path": str(file_path),
            "mime_type": mime_type,
            "file_size": file_size,
            "uploaded_at": datetime.utcnow()
        }

        return document_repo.create(db, document_details)

    def get_documents(self, db: Session, user_id: str) -> List[MedicalDocument]:
        return document_repo.get_user_documents(db, user_id)

    def delete_document(self, db: Session, user_id: str, id: str) -> MedicalDocument:
        doc = document_repo.get(db, id)
        if not doc or doc.user_id != user_id:
            raise ValueError("Record not found")

        # Delete database record and file from path
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass
        return document_repo.remove(db, id)

health_service = HealthService()
