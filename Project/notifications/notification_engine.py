"""
Notification Engine
===================
Scans user health records and generates in-app notification objects.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.models import Appointment, Vaccination, Medication, DoctorVisit


class NotificationEngine:
    """
    Produces educational, reminder-based notification objects.
    """

    def check_appointment_reminders(self, appointments: List[Appointment]) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        window = now + timedelta(days=7)
        alerts = []
        for a in appointments:
            if a.status in ("Scheduled", "Confirmed", "Requested") and now <= a.appointment_date <= window:
                days_away = (a.appointment_date - now).days
                alerts.append({
                    "type": "APPOINTMENT_REMINDER",
                    "priority": "HIGH" if days_away <= 1 else "MEDIUM",
                    "title": f"Upcoming Appointment ({a.status})",
                    "message": f"You have an appointment with {a.doctor_name} ({a.specialty or 'General'}) in {max(0, days_away)} day(s).",
                    "date": a.appointment_date.isoformat(),
                    "resource_id": a.id,
                })
        return alerts

    def check_vaccination_reminders(self, vaccinations: List[Vaccination]) -> List[Dict[str, Any]]:
        today = datetime.utcnow().date().isoformat()
        alerts = []
        for v in vaccinations:
            if v.status == "Overdue":
                alerts.append({
                    "type": "VACCINATION_OVERDUE",
                    "priority": "HIGH",
                    "title": "Vaccination Overdue",
                    "message": f"Your {v.vaccine_name} vaccination is overdue. Please contact your healthcare provider.",
                    "resource_id": v.id,
                })
            elif v.status == "Due" or (v.next_due_date and v.next_due_date <= today):
                alerts.append({
                    "type": "VACCINATION_DUE",
                    "priority": "MEDIUM",
                    "title": "Vaccination Due",
                    "message": f"Your {v.vaccine_name} vaccination is due. Schedule it at your earliest convenience.",
                    "due_date": v.next_due_date,
                    "resource_id": v.id,
                })
        return alerts

    def check_medication_reminders(self, medications: List[Medication]) -> List[Dict[str, Any]]:
        alerts = []
        for m in medications:
            if m.status == "Active" and m.adherence_rate < 80.0:
                alerts.append({
                    "type": "MEDICATION_ADHERENCE_LOW",
                    "priority": "HIGH" if m.adherence_rate < 60 else "MEDIUM",
                    "title": "Low Medication Adherence",
                    "message": f"Your adherence for '{m.name}' is {m.adherence_rate}%. Consider setting daily reminders.",
                    "medication": m.name,
                    "adherence_rate": m.adherence_rate,
                    "resource_id": m.id,
                })
        return alerts

    def check_annual_checkup_reminder(self, visits: List[DoctorVisit]) -> List[Dict[str, Any]]:
        if not visits:
            return [{
                "type": "ANNUAL_CHECKUP_DUE",
                "priority": "LOW",
                "title": "Annual Health Check Recommended",
                "message": "No doctor visits recorded. Consider scheduling an annual health check-up.",
            }]

        try:
            latest_date = max(datetime.strptime(v.visit_date[:10], "%Y-%m-%d") for v in visits if len(str(v.visit_date)) >= 10)
            months_since = (datetime.utcnow() - latest_date).days / 30
            if months_since >= 11:
                return [{
                    "type": "ANNUAL_CHECKUP_DUE",
                    "priority": "LOW",
                    "title": "Annual Health Check Recommended",
                    "message": f"Your last recorded visit was {int(months_since)} month(s) ago. Consider scheduling a check-up.",
                    "last_visit": latest_date.date().isoformat(),
                }]
        except (ValueError, TypeError):
            pass
        return []

    def get_all_notifications(
        self,
        appointments: List[Appointment],
        vaccinations: List[Vaccination],
        medications: List[Medication],
        visits: List[DoctorVisit],
    ) -> Dict[str, Any]:
        all_alerts = (
            self.check_appointment_reminders(appointments)
            + self.check_vaccination_reminders(vaccinations)
            + self.check_medication_reminders(medications)
            + self.check_annual_checkup_reminder(visits)
        )

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        all_alerts.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))

        return {
            "total_count": len(all_alerts),
            "high_priority": sum(1 for a in all_alerts if a.get("priority") == "HIGH"),
            "notifications": all_alerts,
        }


notification_engine = NotificationEngine()
