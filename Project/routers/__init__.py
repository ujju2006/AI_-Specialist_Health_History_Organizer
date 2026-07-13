from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.doctor import router as doctor_router
from app.routers.admin import router as admin_router
from app.routers.phr import router as phr_router
from app.routers.family import router as family_router
from app.routers.consent import router as consent_router
from app.routers.goals import router as goals_router
from app.routers.export import router as export_router

__all__ = [
    "auth_router", "health_router", "doctor_router", "admin_router",
    "phr_router", "family_router", "consent_router", "goals_router", "export_router"
]
