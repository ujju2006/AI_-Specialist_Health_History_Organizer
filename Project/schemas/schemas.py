from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[str] = Field(None, max_length=10)  # YYYY-MM-DD
    gender: Optional[str] = Field(None, max_length=50)
    # Personal Health Record (PHR) Fields
    insurance_provider: Optional[str] = Field(None, max_length=150)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    blood_group: Optional[str] = Field(None, max_length=10)
    organ_donor_status: Optional[str] = Field("No", max_length=50)  # Yes, No, Registered
    primary_care_physician: Optional[str] = Field(None, max_length=150)
    pcp_contact: Optional[str] = Field(None, max_length=100)
    smoking_status: Optional[str] = Field("Never", max_length=50)   # Never, Former, Current
    alcohol_frequency: Optional[str] = Field("Never", max_length=50)
    exercise_frequency: Optional[str] = Field("Weekly", max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: Optional[str] = Field("Patient", max_length=50)  # For demo signup / initialization

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[str] = Field(None, max_length=10)
    gender: Optional[str] = Field(None, max_length=50)
    insurance_provider: Optional[str] = Field(None, max_length=150)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    blood_group: Optional[str] = Field(None, max_length=10)
    organ_donor_status: Optional[str] = Field(None, max_length=50)
    primary_care_physician: Optional[str] = Field(None, max_length=150)
    pcp_contact: Optional[str] = Field(None, max_length=100)
    smoking_status: Optional[str] = Field(None, max_length=50)
    alcohol_frequency: Optional[str] = Field(None, max_length=50)
    exercise_frequency: Optional[str] = Field(None, max_length=50)

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    role: str = "Patient"
    roles: List[Any] = []

    @field_validator("roles", mode="before")
    @classmethod
    def convert_roles_to_strings(cls, v):
        if not v:
            return []
        return [r.name if hasattr(r, "name") else str(r) for r in v]

    @model_validator(mode="after")
    def sync_primary_role(self):
        if self.roles and len(self.roles) > 0:
            self.role = str(self.roles[0])
        return self

    model_config = ConfigDict(from_attributes=True)

# Notification Preferences Schemas
class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    appointment_reminders: Optional[bool] = None
    medication_reminders: Optional[bool] = None

class NotificationPreferenceResponse(BaseModel):
    user_id: str
    email_enabled: bool
    appointment_reminders: bool
    medication_reminders: bool

    model_config = ConfigDict(from_attributes=True)

# Medical Condition Schemas
class MedicalConditionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    status: str = Field("Active", max_length=50)  # Active, Managed, Resolved
    diagnosed_date: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class MedicalConditionCreate(MedicalConditionBase):
    pass

class MedicalConditionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    diagnosed_date: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class MedicalConditionResponse(MedicalConditionBase):
    id: str
    user_id: str
    version: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)

# Medication Schemas
class MedicationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = Field(None, max_length=10)
    end_date: Optional[str] = Field(None, max_length=10)
    status: str = Field("Active", max_length=50)  # Active, Completed, Discontinued
    adherence_rate: float = Field(100.0, ge=0.0, le=100.0)

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = Field(None, max_length=10)
    end_date: Optional[str] = Field(None, max_length=10)
    status: Optional[str] = Field(None, max_length=50)
    adherence_rate: Optional[float] = Field(None, ge=0.0, le=100.0)

class MedicationResponse(MedicationBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Medication Dose Log Schemas (For Adherence Calendar)
class MedicationDoseLogCreate(BaseModel):
    medication_id: str
    scheduled_date: str = Field(..., max_length=10)  # YYYY-MM-DD
    scheduled_time: Optional[str] = Field(None, max_length=10)
    status: str = Field("Taken", max_length=20)      # Taken, Missed, Skipped
    notes: Optional[str] = Field(None, max_length=255)

class MedicationDoseLogResponse(BaseModel):
    id: str
    user_id: str
    medication_id: str
    scheduled_date: str
    scheduled_time: Optional[str] = None
    taken_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Allergy Schemas
class AllergyBase(BaseModel):
    allergen: str = Field(..., min_length=1, max_length=100)
    reaction: Optional[str] = Field(None, max_length=255)
    severity: str = Field("Mild", max_length=50)  # Mild, Moderate, Severe
    diagnosed_date: Optional[str] = Field(None, max_length=10)

class AllergyCreate(AllergyBase):
    pass

class AllergyUpdate(BaseModel):
    allergen: Optional[str] = Field(None, min_length=1, max_length=100)
    reaction: Optional[str] = Field(None, max_length=255)
    severity: Optional[str] = Field(None, max_length=50)
    diagnosed_date: Optional[str] = Field(None, max_length=10)

class AllergyResponse(AllergyBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Doctor Visit Schemas
class DoctorVisitBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=100)
    specialty: str = Field(..., min_length=1, max_length=100)
    visit_date: str = Field(..., max_length=10)  # YYYY-MM-DD
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

class DoctorVisitCreate(DoctorVisitBase):
    pass

class DoctorVisitUpdate(BaseModel):
    doctor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    visit_date: Optional[str] = Field(None, max_length=10)
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None

class DoctorVisitResponse(DoctorVisitBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Vaccination Schemas
class VaccinationBase(BaseModel):
    vaccine_name: str = Field(..., min_length=1, max_length=100)
    dose_number: Optional[str] = Field(None, max_length=20)
    date_administered: Optional[str] = Field(None, max_length=10)
    next_due_date: Optional[str] = Field(None, max_length=10)
    status: str = Field("Administered", max_length=50)  # Administered, Due, Overdue

class VaccinationCreate(VaccinationBase):
    pass

class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dose_number: Optional[str] = Field(None, max_length=20)
    date_administered: Optional[str] = Field(None, max_length=10)
    next_due_date: Optional[str] = Field(None, max_length=10)
    status: Optional[str] = Field(None, max_length=50)

class VaccinationResponse(VaccinationBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Vitals Schemas
class VitalsBase(BaseModel):
    systolic_bp: Optional[float] = Field(None, description="Systolic Blood Pressure (mmHg)")
    diastolic_bp: Optional[float] = Field(None, description="Diastolic Blood Pressure (mmHg)")
    weight_kg: Optional[float] = Field(None, description="Weight (kg)")
    height_cm: Optional[float] = Field(None, description="Height (cm)")
    blood_sugar_mgdl: Optional[float] = Field(None, description="Blood Sugar (mg/dL)")
    pulse_bpm: Optional[float] = Field(None, description="Pulse Rate (bpm)")
    temperature_c: Optional[float] = Field(None, description="Body Temperature (°C)")
    oxygen_saturation: Optional[float] = Field(None, description="SPO2 (%)")

class VitalsCreate(VitalsBase):
    pass

class VitalsResponse(VitalsBase):
    id: str
    user_id: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Appointment Schemas (With Expanded Lifecycle)
class AppointmentBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)
    appointment_date: datetime
    location: Optional[str] = Field(None, max_length=255)
    status: str = Field("Confirmed", max_length=50)  # Requested -> Confirmed -> Checked In -> Consultation -> Prescription Issued -> Completed
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)
    appointment_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Emergency Contact Schemas
class EmergencyContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    blood_group: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    relationship: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    blood_group: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class EmergencyContactResponse(EmergencyContactBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Document Schemas
class MedicalDocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    file_path: str
    mime_type: str
    file_size: int
    document_type: str = "PDF"
    version_number: int = 1
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Family Medical History Schemas
class FamilyMedicalHistoryBase(BaseModel):
    relationship: str = Field(..., max_length=50)  # Parent, Grandparent, Sibling
    condition_name: str = Field(..., min_length=1, max_length=100)
    age_of_diagnosis: Optional[str] = Field(None, max_length=20)
    genetic_risk_indicator: Optional[str] = Field("Standard Risk", max_length=50)
    notes: Optional[str] = None

class FamilyMedicalHistoryCreate(FamilyMedicalHistoryBase):
    pass

class FamilyMedicalHistoryUpdate(BaseModel):
    relationship: Optional[str] = Field(None, max_length=50)
    condition_name: Optional[str] = Field(None, min_length=1, max_length=100)
    age_of_diagnosis: Optional[str] = Field(None, max_length=20)
    genetic_risk_indicator: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class FamilyMedicalHistoryResponse(FamilyMedicalHistoryBase):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)

# Health Goal Schemas
class HealthGoalBase(BaseModel):
    goal_type: str = Field(..., max_length=50)  # Weight, BMI, Systolic BP, Diastolic BP, Blood Sugar
    target_value: float
    current_value: float
    start_date: str = Field(..., max_length=10)
    target_date: str = Field(..., max_length=10)
    status: str = Field("Active", max_length=50)

class HealthGoalCreate(HealthGoalBase):
    pass

class HealthGoalUpdate(BaseModel):
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    target_date: Optional[str] = None
    status: Optional[str] = None

class HealthGoalResponse(HealthGoalBase):
    id: str
    user_id: str
    progress_percent: int

    model_config = ConfigDict(from_attributes=True)

# Consent & Temporary Data Sharing Schemas
class ConsentShareTokenCreate(BaseModel):
    scope_summary: str = Field("All Records", max_length=255)
    duration_hours: int = Field(24, ge=1, le=720)

class ConsentShareTokenResponse(BaseModel):
    id: str
    user_id: str
    token_hash: str
    scope_summary: str
    created_at: datetime
    expires_at: datetime
    is_revoked: bool
    access_count: int

    model_config = ConfigDict(from_attributes=True)

# My Health Snapshot Schema
class MyHealthSnapshotResponse(BaseModel):
    user_id: str
    patient_name: str
    blood_group: str
    organ_donor_status: str
    primary_care_physician: str
    pcp_contact: str
    allergies: List[str]
    chronic_conditions: List[str]
    active_medications_count: int
    emergency_contact: str
    emergency_contact_phone: str
    latest_vitals: Optional[Dict[str, Any]] = None
    health_score: int
    health_score_label: str

    model_config = ConfigDict(from_attributes=True)

# Analytics & Insights Schemas
class HealthScoreResponse(BaseModel):
    score: int
    label: str  # Excellent, Good, Fair, Attention Required
    components: Dict[str, Any]
    recorded_at: str

class TrendEstimateResponse(BaseModel):
    metric: str
    current_average: float
    historical_average: float
    trend_direction: str  # ↑ Rising, ↓ Falling, Stable
    highest_spike: float
    lowest_value: float
    normal_range_percentage: float
    variability: str
    historical_estimate: str  # Purely historical observation, not a clinical forecast
    educational_factors: List[str]

class EducationalInsightResponse(BaseModel):
    overall_summary: str
    health_score: int
    health_score_label: str
    bullet_insights: List[str]
    educational_suggestions: List[str]
    disclaimer: str = "This information is rule-based and strictly for educational and organizational purposes. It is NOT a medical diagnosis or clinical prescription."

# Admin Dashboard Schemas
class SecurityEventResponse(BaseModel):
    id: str
    event_type: str
    severity: str
    ip_address: Optional[str] = None
    user_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminUserListItem(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    login_attempts: int

    model_config = ConfigDict(from_attributes=True)

# Audit Log Response Schema
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    event_type: str
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Global Search Result Schema
class GlobalSearchResults(BaseModel):
    conditions: List[MedicalConditionResponse]
    medications: List[MedicationResponse]
    vitals: List[VitalsResponse]
    appointments: List[AppointmentResponse]
