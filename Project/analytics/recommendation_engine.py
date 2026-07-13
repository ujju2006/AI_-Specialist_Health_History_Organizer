"""
Analytics Recommendation Engine
===============================
Generates rule-based, educational guidance from analytical trends and risk classifications.
Strictly non-diagnostic.
"""
from typing import List, Dict, Any
from app.analytics.risk_engine import RiskLevel


class RecommendationEngine:
    """
    Produces rule-based recommendations from quantitative risk inputs.
    """

    def generate_recommendations(
        self,
        risk_profile: Dict[str, Any],
        bp_analytics: Dict[str, Any],
        weight_analytics: Dict[str, Any],
        sugar_analytics: Dict[str, Any],
        medication_adherence: float
    ) -> List[Dict[str, str]]:
        """
        Returns structured recommendations with priority levels (High, Medium, Routine).
        """
        recs = []

        # BP
        bp_risk = risk_profile.get("domain_risks", {}).get("blood_pressure", RiskLevel.NORMAL)
        if bp_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            recs.append({
                "category": "Cardiovascular",
                "priority": "High",
                "title": "Monitor Blood Pressure Closely",
                "action": "Your average systolic/diastolic blood pressure is elevated. Reduce dietary sodium and maintain a daily BP log for your primary physician."
            })
        elif bp_analytics.get("trend") == "Rising":
            recs.append({
                "category": "Cardiovascular",
                "priority": "Medium",
                "title": "Upward BP Trend Detected",
                "action": "Your blood pressure shows an upward trajectory over recent readings. Prioritize rest, stress management, and hydration."
            })

        # Sugar
        sugar_risk = risk_profile.get("domain_risks", {}).get("blood_sugar", RiskLevel.NORMAL)
        if sugar_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            recs.append({
                "category": "Metabolic",
                "priority": "High",
                "title": "Glucose Management Required",
                "action": "Blood glucose levels exceed standard fasting thresholds. Focus on low-glycemic foods and discuss glucose monitoring with your doctor."
            })

        # Weight / BMI
        if weight_analytics.get("bmi_category") in ("Overweight", "Obese"):
            recs.append({
                "category": "Fitness & Nutrition",
                "priority": "Medium",
                "title": "Weight Management Strategy",
                "action": "Aiming for 150 minutes of weekly cardiovascular activity can help gradually move BMI toward optimal ranges."
            })

        # Adherence
        if medication_adherence < 80.0:
            recs.append({
                "category": "Medication Adherence",
                "priority": "High",
                "title": "Improve Prescription Adherence",
                "action": f"Current adherence is {round(medication_adherence, 1)}%. Using daily medication alarms or a weekly pill box is strongly recommended."
            })

        # Default routine guidance if optimal
        if not recs:
            recs.append({
                "category": "Preventive Care",
                "priority": "Routine",
                "title": "Maintain Optimal Health Routines",
                "action": "All tracked metrics are within normal health guidelines. Continue regular physical activity, hydration, and annual checkups."
            })

        return recs


recommendation_engine = RecommendationEngine()
