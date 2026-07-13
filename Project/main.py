import logging
import os
import contextlib
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.models import Role
from app.routers import (
    auth_router, health_router, doctor_router, admin_router,
    phr_router, family_router, consent_router, goals_router, export_router
)
from app.middleware.audit import AuditMiddleware
from app.core.seeder import seed_development_demo_accounts

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app.main")

# Limiter configuration
limiter = Limiter(key_func=get_remote_address)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup activities (creating tables, configuring initial seeds).
    """
    logger.info("Starting up HealthVault Pro Enterprise Portal...")
    
    # Ensure tables are built
    Base.metadata.create_all(bind=engine)
    
    # Initialize basic authorization roles & development seeds
    db = SessionLocal()
    try:
        for r_name in ["Patient", "Doctor", "Administrator", "user", "admin"]:
            if not db.query(Role).filter(Role.name == r_name).first():
                db.add(Role(name=r_name, description=f"{r_name} privileges"))
        db.commit()

        # Execute demo seeding ONLY if not in production
        if getattr(settings, "ENVIRONMENT", "development").lower() != "production":
            seed_development_demo_accounts(db)

    except Exception as e:
        db.rollback()
        logger.error(f"Error during startup database initialization: {str(e)}")
    finally:
        db.close()
        
    yield
    logger.info("Shutting down HealthVault Pro Enterprise Portal...")

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Government-grade, enterprise healthcare SaaS portal. "
        "Implements FHIR-inspired interoperability models, soft delete, optimistic concurrency, "
        "dedicated Analytics Engine, Clinical Decision Support (Educational), and multi-role RBAC."
    ),
    version="2.0.0",
    lifespan=lifespan
)

# Setup SlowAPI Limiter state & handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Audit Middleware
app.add_middleware(AuditMiddleware)

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal system error has occurred. Please contact the administrator."},
    )

# Register API Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(doctor_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(phr_router, prefix="/api/v1")
app.include_router(family_router, prefix="/api/v1")
app.include_router(consent_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")


# ─────────────────────────────────────────────────────────────
#  Monitoring Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["Monitoring"])
def health_check():
    """
    Health check endpoint.
    Returns application status and version.
    Suitable for Docker health checks and load balancer probes.
    Target: respond < 50ms.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "environment": getattr(settings, "ENVIRONMENT", "development"),
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    }


@app.get("/metrics", tags=["Monitoring"])
def metrics_placeholder():
    """
    Application statistics overview.
    In production infrastructure, integrate with Prometheus / OpenTelemetry.
    """
    return {
        "status": "active",
        "note": "Integrate with Prometheus client or OpenTelemetry SDK for full infrastructure observability.",
        "application_metrics": [
            "http_requests_total",
            "http_request_duration_seconds",
            "db_query_duration_seconds",
            "active_users_count",
            "error_rate_percent",
        ]
    }

# Resolve Static files paths dynamically (to serve SPA directly from FastAPI)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
frontend_dir = BASE_DIR / "frontend"

if frontend_dir.exists():
    # Mount scripts / style assets
    if (frontend_dir / "css").exists():
        app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
    if (frontend_dir / "js").exists():
        app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    # Direct endpoint to serve UI
    @app.get("/")
    def read_index():
        return FileResponse(frontend_dir / "index.html")

    logger.info(f"Frontend successfully mounted from: {frontend_dir}")
else:
    logger.warning("Frontend folder not detected. Running API mode exclusive.")
