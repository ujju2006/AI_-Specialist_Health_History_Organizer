from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.models import (
    User, Role, Permission, MedicalCondition, Medication,
    Allergy, DoctorVisit, Vaccination, Vitals, Appointment,
    EmergencyContact, MedicalDocument, AuditLog, NotificationPreference,
    PasswordHistory, UserSession, FamilyMedicalHistory, HealthGoal,
    ConsentShareToken, SecurityEvent, MedicationDoseLog
)

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email.lower(), self.model.is_deleted == False).first()

class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        return db.query(self.model).filter(self.model.name == name).first()

class PermissionRepository(BaseRepository[Permission]):
    def __init__(self):
        super().__init__(Permission)

    def get_by_name(self, db: Session, name: str) -> Optional[Permission]:
        return db.query(self.model).filter(self.model.name == name).first()

class MedicalConditionRepository(BaseRepository[MedicalCondition]):
    def __init__(self):
        super().__init__(MedicalCondition)

    def get_user_conditions(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[MedicalCondition]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).offset(skip).limit(limit).all()

class MedicationRepository(BaseRepository[Medication]):
    def __init__(self):
        super().__init__(Medication)

    def get_user_medications(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Medication]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).offset(skip).limit(limit).all()

class MedicationDoseLogRepository(BaseRepository[MedicationDoseLog]):
    def __init__(self):
        super().__init__(MedicationDoseLog)

    def get_user_dose_logs(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[MedicationDoseLog]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(desc(self.model.scheduled_date)).offset(skip).limit(limit).all()

class AllergyRepository(BaseRepository[Allergy]):
    def __init__(self):
        super().__init__(Allergy)

    def get_user_allergies(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Allergy]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).offset(skip).limit(limit).all()

class DoctorVisitRepository(BaseRepository[DoctorVisit]):
    def __init__(self):
        super().__init__(DoctorVisit)

    def get_user_visits(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[DoctorVisit]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(desc(self.model.visit_date)).offset(skip).limit(limit).all()

class VaccinationRepository(BaseRepository[Vaccination]):
    def __init__(self):
        super().__init__(Vaccination)

    def get_user_vaccinations(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Vaccination]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).offset(skip).limit(limit).all()

class VitalsRepository(BaseRepository[Vitals]):
    def __init__(self):
        super().__init__(Vitals)

    def get_user_vitals(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Vitals]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(desc(self.model.recorded_at)).offset(skip).limit(limit).all()

class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

    def get_user_appointments(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Appointment]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(self.model.appointment_date).offset(skip).limit(limit).all()

class EmergencyContactRepository(BaseRepository[EmergencyContact]):
    def __init__(self):
        super().__init__(EmergencyContact)

    def get_user_contacts(self, db: Session, user_id: str) -> List[EmergencyContact]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).all()

class MedicalDocumentRepository(BaseRepository[MedicalDocument]):
    def __init__(self):
        super().__init__(MedicalDocument)

    def get_user_documents(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[MedicalDocument]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(desc(self.model.uploaded_at)).offset(skip).limit(limit).all()

class FamilyMedicalHistoryRepository(BaseRepository[FamilyMedicalHistory]):
    def __init__(self):
        super().__init__(FamilyMedicalHistory)

    def get_user_family_history(self, db: Session, user_id: str) -> List[FamilyMedicalHistory]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).all()

class HealthGoalRepository(BaseRepository[HealthGoal]):
    def __init__(self):
        super().__init__(HealthGoal)

    def get_user_goals(self, db: Session, user_id: str) -> List[HealthGoal]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).all()

class ConsentShareTokenRepository(BaseRepository[ConsentShareToken]):
    def __init__(self):
        super().__init__(ConsentShareToken)

    def get_by_token(self, db: Session, token_hash: str) -> Optional[ConsentShareToken]:
        return db.query(self.model).filter(self.model.token_hash == token_hash, self.model.is_deleted == False, self.model.is_revoked == False).first()

    def get_user_tokens(self, db: Session, user_id: str) -> List[ConsentShareToken]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_deleted == False).order_by(desc(self.model.created_at)).all()

class SecurityEventRepository(BaseRepository[SecurityEvent]):
    def __init__(self):
        super().__init__(SecurityEvent)

    def get_recent_events(self, db: Session, limit: int = 50) -> List[SecurityEvent]:
        return db.query(self.model).order_by(desc(self.model.timestamp)).limit(limit).all()

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_user_logs(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(self.model).filter(self.model.user_id == user_id).order_by(desc(self.model.timestamp)).offset(skip).limit(limit).all()

class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    def __init__(self):
        super().__init__(NotificationPreference)

    def get_by_user_id(self, db: Session, user_id: str) -> Optional[NotificationPreference]:
        return db.query(self.model).filter(self.model.user_id == user_id).first()

class PasswordHistoryRepository(BaseRepository[PasswordHistory]):
    def __init__(self):
        super().__init__(PasswordHistory)

    def get_recent(self, db: Session, user_id: str, limit: int = 5) -> List[PasswordHistory]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .all()
        )

class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self):
        super().__init__(UserSession)

    def get_active_sessions(self, db: Session, user_id: str) -> List[UserSession]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.is_active == True)
            .order_by(desc(self.model.last_used_at))
            .all()
        )

    def get_by_token_hash(self, db: Session, token_hash: str) -> Optional[UserSession]:
        return db.query(self.model).filter(self.model.refresh_token_hash == token_hash).first()

# Global repository instances
user_repo = UserRepository()
role_repo = RoleRepository()
permission_repo = PermissionRepository()
condition_repo = MedicalConditionRepository()
medication_repo = MedicationRepository()
allergy_repo = AllergyRepository()
visit_repo = DoctorVisitRepository()
vaccination_repo = VaccinationRepository()
vitals_repo = VitalsRepository()
appointment_repo = AppointmentRepository()
contact_repo = EmergencyContactRepository()
document_repo = MedicalDocumentRepository()
audit_repo = AuditLogRepository()
pref_repo = NotificationPreferenceRepository()
password_history_repo = PasswordHistoryRepository()
session_repo = UserSessionRepository()
family_repo = FamilyMedicalHistoryRepository()
goal_repo = HealthGoalRepository()
consent_repo = ConsentShareTokenRepository()
security_event_repo = SecurityEventRepository()
dose_log_repo = MedicationDoseLogRepository()
