"""
Insights Recommendation Engine
==============================
Generates educational wellness recommendations and lifestyle suggestions.
"""
from typing import List, Dict, Any, Tuple
from app.models.models import Vitals, Medication


class InsightsRecommendationEngine:
    """
    Produces rule-based educational tips and lifestyle suggestions.
    """

    def generate_tips_and_suggestions(
        self,
        vitals: List[Vitals],
        medications: List[Medication],
        weight_analytics: Dict[str, Any] = None
    ) -> Tuple[List[str], List[str]]:
        wellness = []
        lifestyle = []

        if not vitals:
            return (
                ["Record your blood pressure regularly.", "Log your daily weight for BMI tracking.", "Log your active prescriptions."],
                ["Stay hydrated by drinking 8 glasses of water daily.", "Engage in 150 minutes of moderate activity weekly."]
            )

        latest = vitals[0]

        # Sugar
        if latest.blood_sugar_mgdl is not None:
            if latest.blood_sugar_mgdl > 120:
                wellness.append("Limit simple sugars and refined carbohydrates in your daily diet.")
                lifestyle.append("A 15-minute gentle walk following main meals can significantly improve glucose clearance.")
            elif latest.blood_sugar_mgdl < 70:
                wellness.append("Ensure regular, balanced meals containing complex carbohydrates and lean proteins.")

        # BP
        if latest.systolic_bp is not None and latest.diastolic_bp is not None:
            if latest.systolic_bp >= 130 or latest.diastolic_bp >= 85:
                wellness.append("Monitor dietary sodium intake, aiming for less than 2,300 mg daily.")
                lifestyle.append("Incorporate daily stress-reduction practices such as deep diaphragmatic breathing or meditation.")
            elif latest.systolic_bp < 90 or latest.diastolic_bp < 60:
                lifestyle.append("Maintain consistent fluid intake and ensure adequate dietary electrolytes.")

        # BMI
        if weight_analytics and "bmi_category" in weight_analytics:
            category = weight_analytics["bmi_category"]
            if category in ("Overweight", "Obese"):
                wellness.append("Target a sustainable, gradual weight reduction of approximately 0.5 kg per week.")
                lifestyle.append("Combine moderate cardiovascular exercise with light resistance training 3-4 times per week.")
            elif category == "Underweight":
                wellness.append("Consult a registered dietitian regarding healthy caloric density and nutrient absorption.")

        # Adherence
        active_meds = [m for m in medications if m.status == "Active"]
        if active_meds:
            avg_adh = sum(m.adherence_rate for m in active_meds) / len(active_meds)
            if avg_adh < 90.0:
                wellness.append("Utilize smartphone alarms or a 7-day pill organizer to maintain consistency with prescribed dosing schedules.")

        # Default
        if not wellness:
            wellness.append("Continue adhering to your balanced nutritional plan and routine hydration goals.")
        if not lifestyle:
            lifestyle.append("Aim for 7 to 8 hours of uninterrupted, restorative sleep every night.")

        return wellness, lifestyle


insights_recommendation_engine = InsightsRecommendationEngine()
