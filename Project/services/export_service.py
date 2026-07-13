"""
Health Data Export Service
==========================
Provides structured data exports (FHIR-inspired JSON and portable summaries)
for patient interoperability, consent sharing, and personal records backup.
"""
from typing import Dict, Any, List
from datetime import datetime
from app.models.models import User, Vitals, Medication, MedicalCondition, Allergy, Vaccination, DoctorVisit, Appointment, EmergencyContact, FamilyMedicalHistory


class ExportService:
    """
    Synthesizes patient records into portable, standardized data bundles.
    """

    def generate_fhir_inspired_bundle(
        self,
        user: User,
        conditions: List[MedicalCondition],
        medications: List[Medication],
        allergies: List[Allergy],
        vitals: List[Vitals],
        vaccinations: List[Vaccination],
        visits: List[DoctorVisit],
        appointments: List[Appointment],
        contacts: List[EmergencyContact],
        family_histories: List[FamilyMedicalHistory]
    ) -> Dict[str, Any]:
        """
        Produces an HL7 FHIR-inspired JSON bundle representing the patient's entire health record.
        Not a certified FHIR implementation, but formatted with standard resources and codes for interoperability.
        """
        now = datetime.utcnow().isoformat()
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": now,
            "meta": {
                "versionId": "1",
                "lastUpdated": now,
                "note": "Health data models are designed with concepts inspired by the HL7 FHIR standard to improve interoperability and future extensibility. This project is not a certified FHIR implementation."
            },
            "entry": []
        }

        # 1. Patient Resource
        bundle["entry"].append({
            "resource": {
                "resourceType": "Patient",
                "id": user.id,
                "name": [{"use": "official", "family": user.last_name or "", "given": [user.first_name or ""]}],
                "telecom": [
                    {"system": "email", "value": user.email},
                    {"system": "phone", "value": user.phone_number or ""}
                ],
                "gender": user.gender or "unknown",
                "birthDate": user.date_of_birth or "",
                "extension": [
                    {"url": "http://healthvault.pro/fhir/StructureDefinition/bloodGroup", "valueString": user.blood_group or "Unknown"},
                    {"url": "http://healthvault.pro/fhir/StructureDefinition/organDonorStatus", "valueString": user.organ_donor_status or "No"},
                    {"url": "http://healthvault.pro/fhir/StructureDefinition/insuranceProvider", "valueString": user.insurance_provider or "None"},
                    {"url": "http://healthvault.pro/fhir/StructureDefinition/primaryCarePhysician", "valueString": user.primary_care_physician or "None"}
                ]
            }
        })

        # 2. Conditions
        for c in conditions:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Condition",
                    "id": c.id,
                    "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": c.status.lower()}]},
                    "code": {"text": c.name},
                    "subject": {"reference": f"Patient/{user.id}"},
                    "onsetDateTime": c.diagnosed_date or "",
                    "note": [{"text": c.notes or ""}]
                }
            })

        # 3. Medications
        for m in medications:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": m.id,
                    "status": "active" if m.status == "Active" else "completed",
                    "medicationCodeableConcept": {"text": m.name},
                    "subject": {"reference": f"Patient/{user.id}"},
                    "dosage": [{"text": f"{m.dosage or ''} - {m.frequency or ''}"}],
                    "effectivePeriod": {"start": m.start_date or "", "end": m.end_date or ""}
                }
            })

        # 4. Allergies
        for al in allergies:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "AllergyIntolerance",
                    "id": al.id,
                    "type": "allergy",
                    "criticality": "high" if al.severity == "Severe" else ("low" if al.severity == "Mild" else "unable-to-assess"),
                    "code": {"text": al.allergen},
                    "patient": {"reference": f"Patient/{user.id}"},
                    "reaction": [{"description": al.reaction or ""}]
                }
            })

        # 5. Vitals (Observations)
        for v in vitals:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "id": v.id,
                    "status": "final",
                    "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs", "display": "Vital Signs"}]}],
                    "effectiveDateTime": v.recorded_at.isoformat() if v.recorded_at else "",
                    "component": [
                        {"code": {"text": "Systolic Blood Pressure"}, "valueQuantity": {"value": v.systolic_bp, "unit": "mmHg"}} if v.systolic_bp else None,
                        {"code": {"text": "Diastolic Blood Pressure"}, "valueQuantity": {"value": v.diastolic_bp, "unit": "mmHg"}} if v.diastolic_bp else None,
                        {"code": {"text": "Body Weight"}, "valueQuantity": {"value": v.weight_kg, "unit": "kg"}} if v.weight_kg else None,
                        {"code": {"text": "Blood Glucose"}, "valueQuantity": {"value": v.blood_sugar_mgdl, "unit": "mg/dL"}} if v.blood_sugar_mgdl else None,
                        {"code": {"text": "Heart Rate"}, "valueQuantity": {"value": v.pulse_bpm, "unit": "bpm"}} if v.pulse_bpm else None
                    ]
                }
            })
            # Clean None components
            bundle["entry"][-1]["resource"]["component"] = [comp for comp in bundle["entry"][-1]["resource"]["component"] if comp is not None]

        # 6. Vaccinations (Immunizations)
        for vac in vaccinations:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Immunization",
                    "id": vac.id,
                    "status": "completed" if vac.status == "Administered" else "entered-in-error",
                    "vaccineCode": {"text": vac.vaccine_name},
                    "patient": {"reference": f"Patient/{user.id}"},
                    "occurrenceDateTime": vac.date_administered or vac.next_due_date or ""
                }
            })

        # 7. Family Medical History
        for fm in family_histories:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "FamilyMemberHistory",
                    "id": fm.id,
                    "status": "completed",
                    "patient": {"reference": f"Patient/{user.id}"},
                    "relationship": {"text": fm.relationship},
                    "condition": [{"code": {"text": fm.condition_name}, "onsetAge": {"text": fm.age_of_diagnosis or ""}}]
                }
            })

        return bundle

    def generate_portable_summary(
        self,
        user: User,
        conditions: List[MedicalCondition],
        medications: List[Medication],
        allergies: List[Allergy],
        vitals: List[Vitals],
        contacts: List[EmergencyContact]
    ) -> Dict[str, Any]:
        """
        Produces a clean, human-readable summary structure ideal for printing, PDF generation, or emergency access.
        """
        latest_vitals = {}
        if vitals:
            v = vitals[0]
            latest_vitals = {
                "recorded_at": v.recorded_at.isoformat() if v.recorded_at else "N/A",
                "blood_pressure": f"{v.systolic_bp}/{v.diastolic_bp} mmHg" if (v.systolic_bp and v.diastolic_bp) else "N/A",
                "weight_kg": v.weight_kg,
                "blood_sugar_mgdl": v.blood_sugar_mgdl,
                "pulse_bpm": v.pulse_bpm,
                "spo2_pct": v.oxygen_saturation
            }

        return {
            "title": "Patient Clinical Health Summary",
            "generated_at": datetime.utcnow().isoformat(),
            "patient": {
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                "email": user.email,
                "date_of_birth": user.date_of_birth or "N/A",
                "blood_group": user.blood_group or "Not specified",
                "organ_donor_status": user.organ_donor_status or "No",
                "insurance_provider": user.insurance_provider or "None on file",
                "primary_care_physician": user.primary_care_physician or "None on file"
            },
            "emergency_contacts": [
                {"name": ec.name, "relationship": ec.relationship, "phone": ec.phone_number}
                for ec in contacts
            ],
            "allergies": [
                {"allergen": al.allergen, "severity": al.severity, "reaction": al.reaction}
                for al in allergies
            ],
            "active_conditions": [
                {"condition": c.name, "status": c.status, "diagnosed": c.diagnosed_date}
                for c in conditions if c.status == "Active"
            ],
            "active_medications": [
                {"medication": m.name, "dosage": m.dosage, "frequency": m.frequency, "adherence_rate": f"{m.adherence_rate}%"}
                for m in medications if m.status == "Active"
            ],
            "latest_vitals": latest_vitals
        }


export_service = ExportService()
