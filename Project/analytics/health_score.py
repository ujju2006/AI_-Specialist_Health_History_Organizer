"""
Health Score Engine
===================
Calculates a 0-100 personal health score from the latest vitals and medication adherence.
Provides detailed component attribution showing exactly where points were deducted.
"""
from typing import List, Dict, Any, Optional
from app.models.models import Vitals, Medication


class HealthScoreEngine:
    """
    Computes health scores and component breakdown.
    """

    def calculate_health_score(self, vitals: List[Vitals], medications: Optional[List[Medication]] = None) -> Dict[str, Any]:
        """
        Calculates a 0-100 personal health score and returns the score, classification label,
        and detailed component deductions.
        """
        if not vitals:
            return {
                "score": 75,
                "label": "Good (Default Baseline)",
                "components": {"note": "No vital signs recorded yet. Showing default baseline."},
                "recorded_at": "N/A"
            }

        latest = vitals[0]
        penalties: Dict[str, int] = {}
        total_penalty = 0

        # 1. Systolic BP (Normal: 90-120)
        if latest.systolic_bp is not None:
            if latest.systolic_bp > 140 or latest.systolic_bp < 85:
                penalties["Blood Pressure (Systolic)"] = 15
                total_penalty += 15
            elif latest.systolic_bp > 120 or latest.systolic_bp < 90:
                penalties["Blood Pressure (Systolic)"] = 5
                total_penalty += 5

        # 2. Diastolic BP (Normal: 60-80)
        if latest.diastolic_bp is not None:
            if latest.diastolic_bp > 90 or latest.diastolic_bp < 55:
                penalties["Blood Pressure (Diastolic)"] = 15
                total_penalty += 15
            elif latest.diastolic_bp > 80 or latest.diastolic_bp < 60:
                penalties["Blood Pressure (Diastolic)"] = 5
                total_penalty += 5

        # 3. Blood Sugar fasting (Normal: 70-100 mg/dL)
        if latest.blood_sugar_mgdl is not None:
            if latest.blood_sugar_mgdl > 140 or latest.blood_sugar_mgdl < 60:
                penalties["Blood Sugar"] = 20
                total_penalty += 20
            elif latest.blood_sugar_mgdl > 100 or latest.blood_sugar_mgdl < 70:
                penalties["Blood Sugar"] = 8
                total_penalty += 8

        # 4. Pulse (Normal: 60-100 bpm)
        if latest.pulse_bpm is not None:
            if latest.pulse_bpm > 110 or latest.pulse_bpm < 50:
                penalties["Resting Pulse"] = 10
                total_penalty += 10
            elif latest.pulse_bpm > 100 or latest.pulse_bpm < 60:
                penalties["Resting Pulse"] = 3
                total_penalty += 3

        # 5. SpO2 (Normal: 95-100%)
        if latest.oxygen_saturation is not None:
            if latest.oxygen_saturation < 90:
                penalties["Oxygen Saturation"] = 20
                total_penalty += 20
            elif latest.oxygen_saturation < 95:
                penalties["Oxygen Saturation"] = 10
                total_penalty += 10

        # 6. Temperature (Normal: 36.1-37.2°C)
        if latest.temperature_c is not None:
            if latest.temperature_c > 38.0 or latest.temperature_c < 35.5:
                penalties["Body Temperature"] = 10
                total_penalty += 10
            elif latest.temperature_c > 37.2 or latest.temperature_c < 36.1:
                penalties["Body Temperature"] = 3
                total_penalty += 3

        # 7. Medication Adherence
        if medications:
            active_meds = [m for m in medications if m.status == "Active"]
            if active_meds:
                avg_adherence = sum(m.adherence_rate for m in active_meds) / len(active_meds)
                if avg_adherence < 70.0:
                    penalties["Medication Adherence"] = 15
                    total_penalty += 15
                elif avg_adherence < 85.0:
                    penalties["Medication Adherence"] = 8
                    total_penalty += 8

        score = max(30, min(100, 100 - total_penalty))
        label = self.classify_score(score)

        return {
            "score": score,
            "label": label,
            "components": penalties if penalties else {"All Vitals": "Optimal Range (+0 deductions)"},
            "recorded_at": latest.recorded_at.isoformat() if latest.recorded_at else "N/A"
        }

    def classify_score(self, score: int) -> str:
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        elif score >= 40:
            return "Attention Required"
        else:
            return "Critical Action Needed"


health_score_engine = HealthScoreEngine()
