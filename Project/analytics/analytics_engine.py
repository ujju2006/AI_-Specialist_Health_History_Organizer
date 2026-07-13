"""
Master Analytics Engine
=======================
Orchestrator combining TrendEngine, HealthScoreEngine, RiskEngine,
RecommendationEngine, and TimelineEngine into a unified analytical interface.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.models import Vitals, Medication, Vaccination, DoctorVisit, Appointment, MedicalDocument
from app.analytics.trend_engine import trend_engine
from app.analytics.health_score import health_score_engine
from app.analytics.risk_engine import risk_engine, RiskLevel
from app.analytics.recommendation_engine import recommendation_engine
from app.analytics.timeline_engine import timeline_engine


class AnalyticsEngine:
    """
    Unified analytics facade coordinating domain sub-engines.
    """

    def calculate_health_score(self, vitals: List[Vitals], medications: Optional[List[Medication]] = None) -> int:
        res = health_score_engine.calculate_health_score(vitals, medications)
        return res["score"]

    def get_detailed_health_score(self, vitals: List[Vitals], medications: Optional[List[Medication]] = None) -> Dict[str, Any]:
        return health_score_engine.calculate_health_score(vitals, medications)

    def classify_health_score(self, score: int) -> str:
        return health_score_engine.classify_score(score)

    def get_bp_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.systolic_bp is not None and v.diastolic_bp is not None]
        if not records:
            return {"status": "No data"}

        sys_tuples = [(v.recorded_at, v.systolic_bp) for v in records if v.recorded_at and v.systolic_bp]
        trend_res = trend_engine.analyze_metric_trend(sys_tuples, "Systolic Blood Pressure", 90.0, 120.0, 140.0)

        systolics = [r.systolic_bp for r in records]
        diastolics = [r.diastolic_bp for r in records]

        spikes = [
            {"date": r.recorded_at.isoformat(), "systolic": r.systolic_bp, "diastolic": r.diastolic_bp}
            for r in records if r.systolic_bp >= 140 or r.diastolic_bp >= 90
        ]

        normal_count = sum(1 for r in records if 90 <= r.systolic_bp <= 120 and 60 <= r.diastolic_bp <= 80)
        normal_pct = round((normal_count / len(records)) * 100, 1)

        avg_sys = round(sum(systolics) / len(systolics), 1)
        avg_dia = round(sum(diastolics) / len(diastolics), 1)
        risk = risk_engine.classify_bp_risk(avg_sys, avg_dia)

        now = datetime.utcnow()
        monthly_series = [
            {"date": r.recorded_at.date().isoformat(), "systolic": r.systolic_bp, "diastolic": r.diastolic_bp}
            for r in records if r.recorded_at >= now - timedelta(days=30)
        ]

        return {
            "highest_systolic": max(systolics),
            "lowest_systolic": min(systolics),
            "avg_systolic": avg_sys,
            "highest_diastolic": max(diastolics),
            "lowest_diastolic": min(diastolics),
            "avg_diastolic": avg_dia,
            "trend": trend_res["trend_direction"].split()[-1] if " " in trend_res["trend_direction"] else trend_res["trend_direction"],
            "trend_details": trend_res,
            "risk_level": risk,
            "spike_detected": len(spikes) > 0,
            "spikes_logged": spikes[:5],
            "normal_range_pct": normal_pct,
            "monthly_series": monthly_series[-30:]
        }

    def get_weight_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.weight_kg is not None and v.height_cm is not None]
        if not records:
            return {"status": "No data"}

        latest = records[0]
        weight = latest.weight_kg
        height_m = latest.height_cm / 100.0
        bmi = round(weight / (height_m ** 2), 1) if height_m > 0 else 0.0

        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        now = datetime.utcnow()
        week_records = [r for r in records if r.recorded_at >= now - timedelta(days=7)]
        month_records = [r for r in records if r.recorded_at >= now - timedelta(days=30)]

        weekly_change = round(week_records[0].weight_kg - week_records[-1].weight_kg, 2) if len(week_records) >= 2 else 0.0
        monthly_change = round(month_records[0].weight_kg - month_records[-1].weight_kg, 2) if len(month_records) >= 2 else 0.0

        weight_series = [
            {"date": r.recorded_at.date().isoformat(), "weight_kg": r.weight_kg}
            for r in reversed(records[-30:])
        ]

        wt_tuples = [(v.recorded_at, v.weight_kg) for v in records if v.recorded_at and v.weight_kg]
        trend_res = trend_engine.analyze_metric_trend(wt_tuples, "Weight (kg)", 50.0, 90.0)

        return {
            "current_weight": weight,
            "height_cm": latest.height_cm,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "weekly_change_kg": weekly_change,
            "monthly_change_kg": monthly_change,
            "healthy_range_min": round(18.5 * (height_m ** 2), 1),
            "healthy_range_max": round(24.9 * (height_m ** 2), 1),
            "trend": "Decreasing" if monthly_change < 0 else ("Increasing" if monthly_change > 0 else "Stable"),
            "trend_details": trend_res,
            "weight_series": weight_series
        }

    def get_sugar_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.blood_sugar_mgdl is not None]
        if not records:
            return {"status": "No data"}

        levels = [r.blood_sugar_mgdl for r in records]
        sug_tuples = [(v.recorded_at, v.blood_sugar_mgdl) for v in records if v.recorded_at and v.blood_sugar_mgdl]
        trend_res = trend_engine.analyze_metric_trend(sug_tuples, "Fasting Blood Glucose", 70.0, 100.0, 140.0)

        avg = round(sum(levels) / len(levels), 1)
        risk = risk_engine.classify_sugar_risk(avg)

        sugar_series = [
            {"date": r.recorded_at.date().isoformat(), "blood_sugar_mgdl": r.blood_sugar_mgdl}
            for r in reversed(records[-30:])
        ]

        return {
            "highest": max(levels),
            "lowest": min(levels),
            "average": avg,
            "trend": trend_res["trend_direction"].split()[-1] if " " in trend_res["trend_direction"] else trend_res["trend_direction"],
            "trend_details": trend_res,
            "risk_level": risk,
            "normal_range_description": "Fasting: 70-100 mg/dL. Post-Meal: < 140 mg/dL.",
            "sugar_series": sugar_series
        }

    def get_pulse_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.pulse_bpm is not None]
        if not records:
            return {"status": "No data"}

        pulses = [r.pulse_bpm for r in records]
        resting_sample = sorted(pulses)[:3]
        resting_hr = round(sum(resting_sample) / len(resting_sample), 1)

        pulse_series = [
            {"date": r.recorded_at.date().isoformat(), "pulse_bpm": r.pulse_bpm}
            for r in reversed(records[-30:])
        ]

        p_tuples = [(v.recorded_at, v.pulse_bpm) for v in records if v.recorded_at and v.pulse_bpm]
        trend_res = trend_engine.analyze_metric_trend(p_tuples, "Resting Heart Rate", 60.0, 100.0)

        return {
            "highest": max(pulses),
            "lowest": min(pulses),
            "avg_bpm": round(sum(pulses) / len(pulses), 1),
            "resting_pulse_estimate": resting_hr,
            "trend": trend_res["trend_direction"].split()[-1] if " " in trend_res["trend_direction"] else trend_res["trend_direction"],
            "trend_details": trend_res,
            "pulse_series": pulse_series
        }

    def get_oxygen_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.oxygen_saturation is not None]
        if not records:
            return {"status": "No data"}

        levels = [r.oxygen_saturation for r in records]
        avg = round(sum(levels) / len(levels), 1)
        risk = RiskLevel.NORMAL if avg >= 95 else (RiskLevel.HIGH if avg >= 90 else RiskLevel.CRITICAL)

        o_tuples = [(v.recorded_at, v.oxygen_saturation) for v in records if v.recorded_at and v.oxygen_saturation]
        trend_res = trend_engine.analyze_metric_trend(o_tuples, "Oxygen Saturation (SpO2)", 95.0, 100.0)

        return {
            "highest": max(levels),
            "lowest": min(levels),
            "avg_spo2": avg,
            "risk_level": risk,
            "trend": trend_res["trend_direction"].split()[-1] if " " in trend_res["trend_direction"] else trend_res["trend_direction"]
        }

    def get_temperature_analytics(self, vitals: List[Vitals]) -> Dict[str, Any]:
        records = [v for v in vitals if v.temperature_c is not None]
        if not records:
            return {"status": "No data"}

        temps = [r.temperature_c for r in records]
        return {
            "highest": max(temps),
            "lowest": min(temps),
            "avg_temp": round(sum(temps) / len(temps), 1),
            "trend": "Stable"
        }

    def get_medication_adherence(self, medications: List[Medication]) -> Dict[str, Any]:
        active_meds = [m for m in medications if m.status == "Active"]
        if not active_meds:
            return {"active_count": 0, "overall_adherence": 100.0, "med_list": []}

        adherences = [m.adherence_rate for m in active_meds]
        overall = round(sum(adherences) / len(adherences), 1)

        return {
            "active_count": len(active_meds),
            "overall_adherence": overall,
            "missed_estimates_pct": round(100.0 - overall, 1),
            "adherence_risk": RiskLevel.NORMAL if overall >= 90 else (RiskLevel.BORDERLINE if overall >= 75 else RiskLevel.HIGH),
            "med_list": [
                {"name": m.name, "dosage": m.dosage, "frequency": m.frequency, "adherence": m.adherence_rate}
                for m in active_meds
            ]
        }

    def get_vaccination_summary(self, vaccines: List[Vaccination]) -> Dict[str, Any]:
        now = datetime.utcnow().date()
        completed = [v for v in vaccines if v.status == "Administered"]
        due = [v for v in vaccines if v.status == "Due"]
        overdue = [v for v in vaccines if v.status == "Overdue"]

        upcoming = [
            {"name": v.vaccine_name, "due_date": v.next_due_date}
            for v in vaccines
            if v.next_due_date and v.next_due_date >= now.isoformat()
        ]
        upcoming.sort(key=lambda x: x["due_date"])

        return {
            "completed_count": len(completed),
            "due_count": len(due),
            "overdue_count": len(overdue),
            "total_count": len(vaccines),
            "upcoming_vaccinations": upcoming[:5]
        }

    def get_visit_summary(self, visits: List[DoctorVisit]) -> Dict[str, Any]:
        if not visits:
            return {"total_visits": 0, "by_specialty": {}, "annual_log": {}}

        specialties: Dict[str, int] = {}
        annual: Dict[str, int] = {}

        for v in visits:
            spec = v.specialty or "General Practice"
            specialties[spec] = specialties.get(spec, 0) + 1
            year = v.visit_date[:4] if len(v.visit_date) >= 4 else "Unknown"
            annual[year] = annual.get(year, 0) + 1

        return {
            "total_visits": len(visits),
            "by_specialty": specialties,
            "annual_log": annual
        }

    def get_appointment_timeline(self, appointments: List[Appointment]) -> Dict[str, Any]:
        now = datetime.utcnow()
        upcoming = [a for a in appointments if a.appointment_date >= now and a.status in ("Scheduled", "Confirmed", "Requested")]
        upcoming.sort(key=lambda a: a.appointment_date)

        past = [a for a in appointments if a.appointment_date < now or a.status == "Completed"]

        return {
            "total": len(appointments),
            "upcoming_count": len(upcoming),
            "past_count": len(past),
            "next_appointment": {
                "doctor": upcoming[0].doctor_name,
                "specialty": upcoming[0].specialty,
                "date": upcoming[0].appointment_date.isoformat(),
                "location": upcoming[0].location
            } if upcoming else None,
            "upcoming": [
                {
                    "doctor": a.doctor_name,
                    "specialty": a.specialty,
                    "date": a.appointment_date.isoformat(),
                    "location": a.location,
                    "status": a.status
                }
                for a in upcoming[:5]
            ]
        }

    def get_weekly_summary(self, vitals: List[Vitals]) -> Dict[str, Any]:
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        weekly = [v for v in vitals if v.recorded_at >= week_ago]

        if not weekly:
            return {"status": "No readings this week", "readings_count": 0}

        readings = len(weekly)
        avg_sys = round(sum(v.systolic_bp for v in weekly if v.systolic_bp) / max(1, sum(1 for v in weekly if v.systolic_bp)), 1)
        avg_weight = round(sum(v.weight_kg for v in weekly if v.weight_kg) / max(1, sum(1 for v in weekly if v.weight_kg)), 1)
        avg_sugar = round(sum(v.blood_sugar_mgdl for v in weekly if v.blood_sugar_mgdl) / max(1, sum(1 for v in weekly if v.blood_sugar_mgdl)), 1)

        return {
            "readings_count": readings,
            "avg_systolic_bp": avg_sys,
            "avg_weight_kg": avg_weight,
            "avg_blood_sugar": avg_sugar,
            "period": f"{week_ago.date().isoformat()} to {now.date().isoformat()}"
        }

    def get_unified_timeline(
        self,
        vitals: List[Vitals],
        medications: List[Medication],
        vaccinations: List[Vaccination],
        visits: List[DoctorVisit],
        appointments: List[Appointment],
        documents: Optional[List[MedicalDocument]] = None
    ) -> List[Dict[str, Any]]:
        return timeline_engine.generate_timeline(
            vitals=vitals,
            medications=medications,
            vaccinations=vaccinations,
            visits=visits,
            appointments=appointments,
            documents=documents or []
        )

    def get_comprehensive_analytics(
        self,
        vitals: List[Vitals],
        medications: List[Medication],
        vaccinations: List[Vaccination],
        visits: List[DoctorVisit],
        appointments: List[Appointment],
        documents: Optional[List[MedicalDocument]] = None
    ) -> Dict[str, Any]:
        """
        Returns a master analytics dictionary covering all health dimensions.
        """
        score_info = self.get_detailed_health_score(vitals, medications)
        bp_info = self.get_bp_analytics(vitals)
        wt_info = self.get_weight_analytics(vitals)
        sug_info = self.get_sugar_analytics(vitals)
        adh_info = self.get_medication_adherence(medications)
        risk_info = risk_engine.evaluate_overall_risk(vitals, medications)
        recs = recommendation_engine.generate_recommendations(
            risk_profile=risk_info,
            bp_analytics=bp_info,
            weight_analytics=wt_info,
            sugar_analytics=sug_info,
            medication_adherence=adh_info.get("overall_adherence", 100.0)
        )
        timeline = self.get_unified_timeline(vitals, medications, vaccinations, visits, appointments, documents)

        return {
            "health_score": score_info,
            "risk_profile": risk_info,
            "recommendations": recs,
            "blood_pressure": bp_info,
            "weight_bmi": wt_info,
            "blood_sugar": sug_info,
            "medication_adherence": adh_info,
            "vaccination_summary": self.get_vaccination_summary(vaccinations),
            "visit_summary": self.get_visit_summary(visits),
            "appointment_timeline": self.get_appointment_timeline(appointments),
            "unified_timeline": timeline[:15]
        }


analytics_engine = AnalyticsEngine()
