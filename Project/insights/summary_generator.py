"""
Summary Generator
=================
Generates human-readable, educational narrative summaries of health trends.
"""
from typing import List, Dict, Any
from app.models.models import Vitals, Medication


class SummaryGenerator:
    """
    Produces rule-based text narratives based on analytical vitals data.
    """

    def generate_narrative_summary(
        self,
        vitals: List[Vitals],
        medications: List[Medication],
        bp_analytics: Dict[str, Any] = None,
        weight_analytics: Dict[str, Any] = None,
        sugar_analytics: Dict[str, Any] = None
    ) -> List[str]:
        insights = []

        if not vitals:
            return ["Welcome to HealthVault Pro! Begin logging your vital signs and prescriptions to generate personalized educational health summaries."]

        latest = vitals[0]

        # 1. Glucose
        if latest.blood_sugar_mgdl is not None:
            if latest.blood_sugar_mgdl > 120:
                insights.append("Your latest blood glucose reading is elevated compared to standard fasting guidelines.")
            elif latest.blood_sugar_mgdl < 70:
                insights.append("Your latest blood glucose reading is below the standard fasting threshold.")

        # 2. Blood Pressure
        if latest.systolic_bp is not None and latest.diastolic_bp is not None:
            if latest.systolic_bp >= 130 or latest.diastolic_bp >= 85:
                insights.append("Your recent blood pressure readings indicate Stage 1/Stage 2 elevation.")
            elif latest.systolic_bp < 90 or latest.diastolic_bp < 60:
                insights.append("Your recent blood pressure is tracking lower than standard baseline ranges.")

        # 3. BP Trend
        if bp_analytics and bp_analytics.get("trend") in ("Rising", "↑ Rising"):
            insights.append(f"Noticeable upward trend in systolic blood pressure (Current average: {bp_analytics.get('avg_systolic', 'N/A')} mmHg).")

        # 4. Weight / BMI
        if weight_analytics and "bmi_category" in weight_analytics:
            bmi = weight_analytics.get("bmi", 0)
            category = weight_analytics["bmi_category"]
            if category in ("Overweight", "Obese"):
                insights.append(f"Calculated BMI is {bmi} ({category.lower()} range). Gradual lifestyle adjustments are encouraged.")
            elif category == "Underweight":
                insights.append(f"Calculated BMI is {bmi} (underweight range). Nutritional review is recommended.")

        # 5. Sugar Trend
        if sugar_analytics and sugar_analytics.get("trend") in ("Rising", "↑ Rising"):
            insights.append(f"Fasting blood glucose demonstrates an upward trajectory over recent recordings (Average: {sugar_analytics.get('average', 'N/A')} mg/dL).")

        # 6. Adherence
        active_meds = [m for m in medications if m.status == "Active"]
        if active_meds:
            avg_adh = sum(m.adherence_rate for m in active_meds) / len(active_meds)
            if avg_adh < 85.0:
                insights.append(f"Overall prescription adherence is currently at {round(avg_adh, 1)}%. Consistent daily dosing is essential for therapeutic efficacy.")

        if not insights:
            insights.append("All tracked biological parameters are currently within normal health guidelines. Excellent routine maintenance!")

        return insights


summary_generator = SummaryGenerator()
