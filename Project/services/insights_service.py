"""
Insights Service Facade (Backwards Compatibility)
=================================================
Proxies requests to the modular package located at app.insights.insight_generator.
"""
from app.insights.insight_generator import insight_generator, InsightGenerator, DISCLAIMER

insights_service = insight_generator

__all__ = ["insights_service", "insight_generator", "InsightGenerator", "DISCLAIMER"]
