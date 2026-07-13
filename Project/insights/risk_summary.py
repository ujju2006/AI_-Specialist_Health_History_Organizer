"""
Risk Summary Generator
======================
Summarizes clinical risk parameters into educational overviews with mandatory non-diagnostic disclaimers.
"""
from typing import Dict, Any, List
from app.analytics.risk_engine import RiskLevel


class RiskSummaryGenerator:
    """
    Synthesizes analytical risk assessments into educational summaries.
    """

    def generate_risk_overview(self, risk_profile: Dict[str, Any]) -> Dict[str, Any]:
        overall = risk_profile.get("overall_risk", RiskLevel.NORMAL)
        flags = risk_profile.get("high_risk_flags", [])

        if overall == RiskLevel.CRITICAL:
            summary = "Multiple or significant vital parameters exceed standard normal thresholds. Prompt review by a licensed primary care physician is strongly advised."
        elif overall == RiskLevel.HIGH:
            summary = "One or more tracked biological metrics indicate elevated risk. Discussing these trends during your next medical consultation is recommended."
        elif overall == RiskLevel.BORDERLINE:
            summary = "Tracked vitals show minor deviations from standard baseline ranges. Proactive lifestyle modifications and routine monitoring are encouraged."
        else:
            summary = "All tracked vital signs and prescription adherence rates are within normal health guidelines."

        return {
            "overall_risk_label": overall,
            "risk_summary_text": summary,
            "flagged_parameters": flags,
            "educational_note": "Risk tiers are computed from mathematical rule-based comparisons against general health guidelines. They do not constitute clinical diagnosis."
        }


risk_summary_generator = RiskSummaryGenerator()
