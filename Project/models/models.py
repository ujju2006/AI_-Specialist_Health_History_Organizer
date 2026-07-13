# Health data models are designed with concepts inspired by the HL7 FHIR standard to improve
# interoperability and future extensibility. This project is not a certified FHIR implementation.

import uuid
from datetime import datetime
import sqlalchemy.orm
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Float, Integer, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

# Association Tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)


class FHIRResourceMixin:
    """
    Enterprise mixin providing HL7 FHIR-inspired auditability, Soft Delete, and Optimistic Locking.
    """
    # Optimistic Locking
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    etag: Mapped[str] = mapped_column(String(64), nullable=True)

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[str] = mapped_column(String(36), nullable=True)


class User(Base, FHIRResourceMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    locked_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Privacy & Compliance: consent tracking and data retention
    data_consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    data_consent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deletion_requested_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Personal Health Record (PHR) Module Attributes
    insurance_provider: Mapped[str] = mapped_column(String(150), nullable=True)
    insurance_policy_number: Mapped[str] = mapped_column(String(100), nullable=True)
    insurance_group_number: Mapped[str] = mapped_column(String(100), nullable=True)
    blood_group: Mapped[str] = mapped_column(String(10), nullable=True)
    organ_donor_status: Mapped[str] = mapped_column(String(50), default="No")  # Yes, No, Registered
    primary_care_physician: Mapped[str] = mapped_column(String(150), nullable=True)
    pcp_contact: Mapped[str] = mapped_column(String(100), nullable=True)
    smoking_status: Mapped[str] = mapped_column(String(50), default="Never")   # Never, Former, Current
    alcohol_frequency: Mapped[str] = mapped_column(String(50), default="Never")
    exercise_frequency: Mapped[str] = mapped_column(String(50), default="Weekly")

    # Relationships
    roles = sqlalchemy.orm.relationship("Role", secondary=user_roles, back_populates="users")
    medical_conditions = sqlalchemy.orm.relationship("MedicalCondition", back_populates="user", cascade="all, delete-orphan")
    medications = sqlalchemy.orm.relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    allergies = sqlalchemy.orm.relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    doctor_visits = sqlalchemy.orm.relationship("DoctorVisit", back_populates="user", cascade="all, delete-orphan")
    vaccinations = sqlalchemy.orm.relationship("Vaccination", back_populates="user", cascade="all, delete-orphan")
    vitals = sqlalchemy.orm.relationship("Vitals", back_populates="user", cascade="all, delete-orphan")
    appointments = sqlalchemy.orm.relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    emergency_contacts = sqlalchemy.orm.relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    medical_documents = sqlalchemy.orm.relationship("MedicalDocument", back_populates="user", cascade="all, delete-orphan")
    audit_logs = sqlalchemy.orm.relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = sqlalchemy.orm.relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    password_history = sqlalchemy.orm.relationship("PasswordHistory", back_populates="user", cascade="all, delete-orphan")
    sessions = sqlalchemy.orm.relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    family_histories = sqlalchemy.orm.relationship("FamilyMedicalHistory", back_populates="user", cascade="all, delete-orphan")
    health_goals = sqlalchemy.orm.relationship("HealthGoal", back_populates="user", cascade="all, delete-orphan")
    consent_tokens = sqlalchemy.orm.relationship("ConsentShareToken", back_populates="user", cascade="all, delete-orphan")
    dose_logs = sqlalchemy.orm.relationship("MedicationDoseLog", back_populates="user", cascade="all, delete-orphan")

    @property
    def primary_role(self) -> str:
        """Returns the highest priority role name assigned to the user."""
        if not self.roles:
            return "Patient"
        role_names = [r.name for r in self.roles]
        if "Administrator" in role_names or "admin" in role_names:
            return "Administrator"
        if "Doctor" in role_names or "doctor" in role_names:
            return "Doctor"
        return "Patient"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    users = sqlalchemy.orm.relationship("User", secondary=user_roles, back_populates="roles")
    permissions = sqlalchemy.orm.relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    roles = sqlalchemy.orm.relationship("Role", secondary=role_permissions, back_populates="permissions")


class MedicalCondition(Base, FHIRResourceMixin):
    __tablename__ = "medical_conditions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Active")  # Active, Managed, Resolved
    diagnosed_date: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="medical_conditions")


class Medication(Base, FHIRResourceMixin):
    __tablename__ = "medications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str] = mapped_column(String(100), nullable=True)
    start_date: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    end_date: Mapped[str] = mapped_column(String(10), nullable=True)    # YYYY-MM-DD
    status: Mapped[str] = mapped_column(String(50), default="Active")   # Active, Completed, Discontinued
    adherence_rate: Mapped[float] = mapped_column(Float, default=100.0)

    user = sqlalchemy.orm.relationship("User", back_populates="medications")
    dose_logs = sqlalchemy.orm.relationship("MedicationDoseLog", back_populates="medication", cascade="all, delete-orphan")


class MedicationDoseLog(Base, FHIRResourceMixin):
    """
    Tracks daily adherence events (taken vs missed doses) to power the Medication Adherence Calendar.
    """
    __tablename__ = "medication_dose_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    medication_id: Mapped[str] = mapped_column(String(36), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    scheduled_time: Mapped[str] = mapped_column(String(10), nullable=True)   # HH:MM AM/PM
    taken_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Taken")         # Taken, Missed, Skipped
    notes: Mapped[str] = mapped_column(String(255), nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="dose_logs")
    medication = sqlalchemy.orm.relationship("Medication", back_populates="dose_logs")


class Allergy(Base, FHIRResourceMixin):
    __tablename__ = "allergies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    allergen: Mapped[str] = mapped_column(String(100), nullable=False)
    reaction: Mapped[str] = mapped_column(String(255), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), default="Mild")  # Mild, Moderate, Severe
    diagnosed_date: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD

    user = sqlalchemy.orm.relationship("User", back_populates="allergies")


class DoctorVisit(Base, FHIRResourceMixin):
    __tablename__ = "doctor_visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    visit_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="doctor_visits")


class Vaccination(Base, FHIRResourceMixin):
    __tablename__ = "vaccinations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vaccine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dose_number: Mapped[str] = mapped_column(String(20), nullable=True)
    date_administered: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    next_due_date: Mapped[str] = mapped_column(String(10), nullable=True)      # YYYY-MM-DD
    status: Mapped[str] = mapped_column(String(50), default="Administered")    # Administered, Due, Overdue

    user = sqlalchemy.orm.relationship("User", back_populates="vaccinations")


class Vitals(Base, FHIRResourceMixin):
    __tablename__ = "vitals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    systolic_bp: Mapped[float] = mapped_column(Float, nullable=True)
    diastolic_bp: Mapped[float] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float] = mapped_column(Float, nullable=True)
    blood_sugar_mgdl: Mapped[float] = mapped_column(Float, nullable=True)
    pulse_bpm: Mapped[float] = mapped_column(Float, nullable=True)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=True)
    oxygen_saturation: Mapped[float] = mapped_column(Float, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="vitals")


class Appointment(Base, FHIRResourceMixin):
    """
    Expanded appointment lifecycle:
    Requested -> Confirmed -> Checked In -> Consultation -> Prescription Issued -> Follow-up Scheduled -> Completed
    """
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=True)
    appointment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Confirmed")
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="appointments")


class EmergencyContact(Base, FHIRResourceMixin):
    __tablename__ = "emergency_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    blood_group: Mapped[str] = mapped_column(String(10), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="emergency_contacts")


class MedicalDocument(Base, FHIRResourceMixin):
    __tablename__ = "medical_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), default="PDF")  # PDF, Prescription, X-Ray, MRI, CT Scan, Lab Report, Insurance
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = sqlalchemy.orm.relationship("User", back_populates="medical_documents")


class FamilyMedicalHistory(Base, FHIRResourceMixin):
    """
    Tracks family conditions for Parents, Grandparents, and Siblings.
    Includes display-only genetic risk indicators.
    """
    __tablename__ = "family_medical_histories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)  # Parent, Grandparent, Sibling
    condition_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age_of_diagnosis: Mapped[str] = mapped_column(String(20), nullable=True)
    genetic_risk_indicator: Mapped[str] = mapped_column(String(50), default="Standard Risk")  # Display only indicator
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user = sqlalchemy.orm.relationship("User", back_populates="family_histories")


class HealthGoal(Base, FHIRResourceMixin):
    """
    User-defined targets (Weight, BMI, Blood Pressure, Blood Sugar).
    """
    __tablename__ = "health_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Weight, BMI, Systolic BP, Diastolic BP, Blood Sugar
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    target_date: Mapped[str] = mapped_column(String(10), nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="Active")   # Active, Achieved, Revised

    user = sqlalchemy.orm.relationship("User", back_populates="health_goals")


class ConsentShareToken(Base, FHIRResourceMixin):
    """
    Temporary shareable read-only summary token for doctors.
    Demonstrates privacy-aware design without external integrations.
    """
    __tablename__ = "consent_share_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    scope_summary: Mapped[str] = mapped_column(String(255), default="All Records")  # Vitals, Conditions, Medications, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    access_count: Mapped[int] = mapped_column(Integer, default=0)

    user = sqlalchemy.orm.relationship("User", back_populates="consent_tokens")


class SecurityEvent(Base):
    """
    Basic application metrics & security event tracking for the Admin Dashboard.
    """
    __tablename__ = "security_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # FAILED_LOGIN, ACCOUNT_LOCKED, SESSION_REVOKED
    severity: Mapped[str] = mapped_column(String(20), default="INFO")                 # INFO, WARNING, CRITICAL
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AuditLog(Base):
    """
    Immutable, comprehensive audit trail.
    Tracks: Who | Did What | To Which Record | From Which Device | At What Time | Old/New Values | IP | Browser | Correlation ID
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)

    # WHO
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=True)

    # WHAT
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=True)

    # WHICH RECORD
    resource_id: Mapped[str] = mapped_column(String(36), nullable=True)

    # CHANGED DATA
    old_value: Mapped[str] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=True)

    # WHERE FROM
    endpoint: Mapped[str] = mapped_column(String(255), nullable=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)
    browser: Mapped[str] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=True)
    location_country: Mapped[str] = mapped_column(String(100), nullable=True)

    # OUTCOME
    status_code: Mapped[int] = mapped_column(Integer, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)

    # WHEN
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user = sqlalchemy.orm.relationship("User", back_populates="audit_logs")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    appointment_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    medication_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    vaccination_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    annual_checkup_reminders: Mapped[bool] = mapped_column(Boolean, default=True)

    user = sqlalchemy.orm.relationship("User", back_populates="notification_preferences")


class PasswordHistory(Base):
    """
    Stores hashed previously-used passwords to enforce password history policy.
    Prevents reuse of the last N passwords.
    """
    __tablename__ = "password_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = sqlalchemy.orm.relationship("User", back_populates="password_history")


class UserSession(Base):
    """
    Device / session management. Tracks active sessions per user for security dashboard.
    Maps to refresh tokens for rotation and revocation.
    """
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    device_info: Mapped[str] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = sqlalchemy.orm.relationship("User", back_populates="sessions")
