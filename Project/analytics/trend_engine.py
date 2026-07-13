"""
Trend Engine
============
Calculates multi-timeframe health statistics, moving averages, highest spikes,
variability, normal range adherence, and historical variance estimates.
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import math
from app.models.models import Vitals


class TrendEngine:
    """
    Mathematical engine responsible for trend analysis across vital signs.
    """

    def _get_timeframe_records(self, records: List[Tuple[datetime, float]], days: int) -> List[float]:
        now = datetime.utcnow()
        cutoff = now - timedelta(days=days)
        return [val for dt, val in records if dt >= cutoff]

    def _calculate_stats(self, values: List[float]) -> Dict[str, Any]:
        if not values:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0, "std_dev": 0.0}
        n = len(values)
        avg = sum(values) / n
        variance = sum((x - avg) ** 2 for x in values) / n if n > 1 else 0.0
        std_dev = math.sqrt(variance)
        return {
            "avg": round(avg, 1),
            "min": round(min(values), 1),
            "max": round(max(values), 1),
            "count": n,
            "std_dev": round(std_dev, 2)
        }

    def analyze_metric_trend(
        self,
        records: List[Tuple[datetime, float]], # List of (timestamp, value)
        metric_name: str,
        normal_min: float,
        normal_max: float,
        spike_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Performs comprehensive statistical trend analysis on any numerical health metric.
        """
        if not records:
            return {
                "metric": metric_name,
                "status": "No Data",
                "current_average": 0.0,
                "historical_average": 0.0,
                "weekly_average": 0.0,
                "monthly_average": 0.0,
                "yearly_average": 0.0,
                "moving_average": 0.0,
                "trend_direction": "Stable",
                "highest_spike": 0.0,
                "lowest_value": 0.0,
                "normal_range_percentage": 0.0,
                "variability": "Low",
                "historical_estimate": "No historical data available to estimate variance.",
                "educational_factors": []
            }

        # Sort chronologically
        sorted_records = sorted(records, key=lambda x: x[0])
        all_values = [val for dt, val in sorted_records]

        overall_stats = self._calculate_stats(all_values)
        weekly_vals = self._get_timeframe_records(sorted_records, 7)
        monthly_vals = self._get_timeframe_records(sorted_records, 30)
        yearly_vals = self._get_timeframe_records(sorted_records, 365)

        weekly_stats = self._calculate_stats(weekly_vals)
        monthly_stats = self._calculate_stats(monthly_vals)
        yearly_stats = self._calculate_stats(yearly_vals)

        # 5-period moving average
        moving_window = all_values[-5:] if len(all_values) >= 5 else all_values
        moving_avg = round(sum(moving_window) / len(moving_window), 1)

        # Trend direction (comparing last 3 vs prior 3 or start vs end)
        if len(all_values) >= 2:
            recent_avg = sum(all_values[-3:]) / len(all_values[-3:])
            prior_avg = sum(all_values[:3]) / len(all_values[:3])
            diff = recent_avg - prior_avg
            if diff >= (overall_stats["std_dev"] * 0.5) or diff > 5.0:
                trend_dir = "↑ Rising"
            elif diff <= -(overall_stats["std_dev"] * 0.5) or diff < -5.0:
                trend_dir = "↓ Falling"
            else:
                trend_dir = "→ Stable"
        else:
            trend_dir = "→ Stable"

        # Normal range percentage
        normal_count = sum(1 for val in all_values if normal_min <= val <= normal_max)
        normal_pct = round((normal_count / len(all_values)) * 100, 1)

        # Variability
        if overall_stats["std_dev"] > 15.0:
            variability = "High Variability"
        elif overall_stats["std_dev"] > 5.0:
            variability = "Moderate Variability"
        else:
            variability = "Low Variability (Stable)"

        # Historical Estimate (Mathematical observation labeled clearly as non-clinical)
        if trend_dir == "→ Stable" and variability == "Low Variability (Stable)":
            estimate = "Historical variance indicates values are likely to remain stable around current average."
        elif trend_dir == "↑ Rising":
            estimate = "Historical trend shows an upward trajectory; monitoring adherence and diet is recommended."
        elif trend_dir == "↓ Falling":
            estimate = "Historical trend shows a downward trajectory toward baseline."
        else:
            estimate = "Historical values show moderate fluctuations around the mean."

        # Educational contributing factors based on metric
        factors = []
        if "Blood Pressure" in metric_name or "Systolic" in metric_name:
            factors = ["Stress & Anxiety", "Dietary Sodium", "Physical Activity Level", "Sleep Quality"]
        elif "Blood Sugar" in metric_name or "Glucose" in metric_name:
            factors = ["Carbohydrate Intake", "Fasting Duration", "Physical Exercise", "Medication Adherence"]
        elif "Weight" in metric_name or "BMI" in metric_name:
            factors = ["Caloric Balance", "Metabolic Rate", "Hydration", "Physical Activity"]
        elif "Pulse" in metric_name or "Heart Rate" in metric_name:
            factors = ["Caffeine Intake", "Cardiovascular Fitness", "Stress", "Rest & Recovery"]
        else:
            factors = ["Hydration", "Rest", "Nutrition", "Daily Activity"]

        return {
            "metric": metric_name,
            "status": "Success",
            "current_average": round(all_values[-1], 1) if all_values else 0.0,
            "historical_average": overall_stats["avg"],
            "weekly_average": weekly_stats["avg"] or overall_stats["avg"],
            "monthly_average": monthly_stats["avg"] or overall_stats["avg"],
            "yearly_average": yearly_stats["avg"] or overall_stats["avg"],
            "moving_average": moving_avg,
            "trend_direction": trend_dir,
            "highest_spike": overall_stats["max"],
            "lowest_value": overall_stats["min"],
            "normal_range_percentage": normal_pct,
            "variability": variability,
            "historical_estimate": estimate,
            "educational_factors": factors
        }


trend_engine = TrendEngine()
