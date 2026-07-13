"""
Notification Engine Facade (Backwards Compatibility)
====================================================
Proxies requests to the modular package located at app.notifications.notification_engine.
"""
from app.notifications.notification_engine import notification_engine, NotificationEngine

__all__ = ["notification_engine", "NotificationEngine"]
