"""
Timeline Engine
===============
Synthesizes events from doctor visits, vaccinations, appointments, prescriptions,
and vital sign spikes into a unified, chronological patient health timeline.
"""
from typing import List, Dict, Any
from datetime import datetime
from app.models.models import Vitals, Medication, Vaccination, DoctorVisit, Appointment, MedicalDocument


class TimelineEngine:
    """
    Aggregates multi-source healthcare events into a unified timeline feed.
    """

    def generate_timeline(
        self,
        vitals: List[Vitals],
        medications: List[Medication],
        vaccinations: List[Vaccination],
        visits: List[DoctorVisit],
        appointments: List[Appointment],
        documents: List[MedicalDocument],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Returns a sorted list of timeline events (newest first).
        """
        events = []

        # 1. Doctor Visits
        for v in visits:
            events.append({
                "id": v.id,
                "type": "Consultation",
                "title": f"Visit with {v.doctor_name}",
                "subtitle": f"Specialty: {v.specialty}",
                "details": v.diagnosis or v.symptoms or "General consultation",
                "timestamp": v.visit_date,
                "icon": "user-md",
                "color": "blue"
            })

        # 2. Appointments
        for a in appointments:
            dt_str = a.appointment_date.isoformat() if isinstance(a.appointment_date, datetime) else str(a.appointment_date)
            events.append({
                "id": a.id,
                "type": "Appointment",
                "title": f"Appointment: {a.doctor_name}",
                "subtitle": a.specialty or "Clinical Consultation",
                "details": f"Status: {a.status} | Location: {a.location or 'Clinic'}",
                "timestamp": dt_str[:10],
                "icon": "calendar",
                "color": "purple" if a.status == "Confirmed" else ("green" if a.status == "Completed" else "gray")
            })

        # 3. Vaccinations
        for vac in vaccinations:
            events.append({
                "id": vac.id,
                "type": "Vaccination",
                "title": f"Vaccine: {vac.vaccine_name}",
                "subtitle": f"Dose: {vac.dose_number or 'Standard'}",
                "details": f"Status: {vac.status}",
                "timestamp": vac.date_administered or vac.next_due_date or "N/A",
                "icon": "syringe",
                "color": "teal"
            })

        # 4. Medications started
        for m in medications:
            if m.start_date:
                events.append({
                    "id": m.id,
                    "type": "Prescription",
                    "title": f"Started Medication: {m.name}",
                    "subtitle": f"Dosage: {m.dosage or 'As prescribed'}",
                    "details": f"Frequency: {m.frequency or 'Daily'} | Status: {m.status}",
                    "timestamp": m.start_date,
                    "icon": "pills",
                    "color": "indigo"
                })

        # 5. Medical Documents Uploaded
        for doc in documents:
            dt_str = doc.uploaded_at.isoformat() if isinstance(doc.uploaded_at, datetime) else str(doc.uploaded_at)
            events.append({
                "id": doc.id,
                "type": "Document",
                "title": f"Uploaded Report: {doc.title}",
                "subtitle": doc.document_type,
                "details": doc.description or "Medical document added to vault",
                "timestamp": dt_str[:10],
                "icon": "file-medical",
                "color": "orange"
            })

        # 6. Vital Spikes / Notable events
        for v in vitals:
            dt_str = v.recorded_at.isoformat() if isinstance(v.recorded_at, datetime) else str(v.recorded_at)
            if v.systolic_bp and (v.systolic_bp >= 140 or v.diastolic_bp >= 90):
                events.append({
                    "id": v.id + "_bp",
                    "type": "Vital Spike",
                    "title": "High Blood Pressure Logged",
                    "subtitle": f"Reading: {v.systolic_bp}/{v.diastolic_bp} mmHg",
                    "details": "Above standard clinical thresholds",
                    "timestamp": dt_str[:10],
                    "icon": "heartbeat",
                    "color": "red"
                })
            elif v.blood_sugar_mgdl and (v.blood_sugar_mgdl >= 140 or v.blood_sugar_mgdl < 65):
                events.append({
                    "id": v.id + "_sugar",
                    "type": "Vital Spike",
                    "title": "Glucose Alert Logged",
                    "subtitle": f"Reading: {v.blood_sugar_mgdl} mg/dL",
                    "details": "Outside normal fasting boundaries",
                    "timestamp": dt_str[:10],
                    "icon": "tint",
                    "color": "red"
                })

        # Sort descending by timestamp string
        events.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return events[:limit]


timeline_engine = TimelineEngine()
