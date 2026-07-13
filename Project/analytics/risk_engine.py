"""
Risk Classification Engine
==========================
Stratifies health metrics into standard risk levels: Normal, Borderline, High, Critical.
Based on standard health monitoring guidelines.
"""
from typing import Dict, Any, List
from app.models.models import Vitals, Medication


class RiskLevel:
    NORMAL = "Normal"
    BORDERLINE = "Borderline"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskEngine:
    """
    Evaluates individual vital signs and aggregate metrics to assign clinical risk tiers.
    """

    def classify_bp_risk(self, systolic: float, diastolic: float) -> str:
        if systolic >= 140 or diastolic >= 90:
            return RiskLevel.CRITICAL
        elif systolic >= 130 or diastolic >= 80:
            return RiskLevel.HIGH
        elif systolic >= 120 and diastolic < 80:
            return RiskLevel.BORDERLINE
        else:
            return RiskLevel.NORMAL

    def classify_sugar_risk(self, fasting_mgdl: float) -> str:
        if fasting_mgdl >= 140 or fasting_mgdl < 60:
            return RiskLevel.CRITICAL
        elif fasting_mgdl >= 100 or fasting_mgdl < 70:
            return RiskLevel.BORDERLINE
        else:
            return RiskLevel.NORMAL

    def classify_bmi_risk(self, bmi: float) -> str:
        if bmi >= 35.0 or bmi < 16.0:
            return RiskLevel.CRITICAL
        elif bmi >= 30.0 or bmi < 18.5:
            return RiskLevel.HIGH
        elif bmi >= 25.0:
            return RiskLevel.BORDERLINE
        else:
            return RiskLevel.NORMAL

    def classify_adherence_risk(self, adherence_rate: float) -> str:
        if adherence_rate < 70.0:
            return RiskLevel.HIGH
        elif adherence_rate < 85.0:
            return RiskLevel.BORDERLINE
        else:
            return RiskLevel.NORMAL

    def evaluate_overall_risk(self, vitals: List[Vitals], medications: List[Medication]) -> Dict[str, Any]:
        """
        Returns a comprehensive risk profile across all tracked vital domains.
        """
        if not vitals:
            return {
                "overall_risk": RiskLevel.NORMAL,
                "domain_risks": {
                    "blood_pressure": RiskLevel.NORMAL,
                    "blood_sugar": RiskLevel.NORMAL,
                    "bmi": RiskLevel.NORMAL,
                    "medication_adherence": RiskLevel.NORMAL
                },
                "high_risk_flags": []
            }

        latest = vitals[0]
        flags = []

        # BP
        bp_risk = RiskLevel.NORMAL
        if latest.systolic_bp and latest.diastolic_bp:
            bp_risk = self.classify_bp_risk(latest.systolic_bp, latest.diastolic_bp)
            if bp_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                flags.append(f"Blood Pressure is {bp_risk.lower()} ({latest.systolic_bp}/{latest.diastolic_bp} mmHg)")

        # Sugar
        sugar_risk = RiskLevel.NORMAL
        if latest.blood_sugar_mgdl:
            sugar_risk = self.classify_sugar_risk(latest.blood_sugar_mgdl)
            if sugar_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                flags.append(f"Blood Glucose is {sugar_risk.lower()} ({latest.blood_sugar_mgdl} mg/dL)")

        # BMI
        bmi_risk = RiskLevel.NORMAL
        if latest.weight_kg and latest.height_cm and latest.height_cm > 0:
            bmi = latest.weight_kg / ((latest.height_cm / 100.0) ** 2)
            bmi_risk = self.classify_bmi_risk(bmi)
            if bmi_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                flags.append(f"BMI is outside normal range ({round(bmi, 1)})")

        # Adherence
        adh_risk = RiskLevel.NORMAL
        active_meds = [m for m in medications if m.status == "Active"]
        if active_meds:
            avg_adh = sum(m.adherence_rate for m in active_meds) / len(active_meds)
            adh_risk = self.classify_adherence_risk(avg_adh)
            if adh_risk == RiskLevel.HIGH:
                flags.append(f"Medication adherence is below 70% ({round(avg_adh, 1)}%)")

        # Aggregate overall
        all_risks = [bp_risk, sugar_risk, bmi_risk, adh_risk]
        if RiskLevel.CRITICAL in all_risks:
            overall = RiskLevel.CRITICAL
        elif RiskLevel.HIGH in all_risks:
            overall = RiskLevel.HIGH
        elif RiskLevel.BORDERLINE in all_risks:
            overall = RiskLevel.BORDERLINE
        else:
            overall = RiskLevel.NORMAL

        return {
            "overall_risk": overall,
            "domain_risks": {
                "blood_pressure": bp_risk,
                "blood_sugar": sugar_risk,
                "bmi": bmi_risk,
                "medication_adherence": adh_risk
            },
            "high_risk_flags": flags
        }


risk_engine = RiskEngine()
