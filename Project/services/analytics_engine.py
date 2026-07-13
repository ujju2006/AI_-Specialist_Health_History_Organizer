"""
Analytics Engine Facade (Backwards Compatibility)
=================================================
Proxies requests to the modular package located at app.analytics.analytics_engine.
"""
from app.analytics.analytics_engine import analytics_engine, AnalyticsEngine
from app.analytics.risk_engine import RiskLevel

__all__ = ["analytics_engine", "AnalyticsEngine", "RiskLevel"]
