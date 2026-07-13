import json
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.database import SessionLocal
from app.models.models import AuditLog

logger = logging.getLogger("app.audit")

# Routes to skip to avoid log bloat
SKIP_PREFIXES = ["/docs", "/redoc", "/openapi.json", "/static", "/health", "/metrics"]

# HTTP method → CRUD action label
METHOD_ACTION_MAP = {
    "GET": "READ",
    "POST": "CREATE",
    "PUT": "UPDATE",
    "PATCH": "UPDATE",
    "DELETE": "DELETE",
}

def _parse_browser(user_agent: str) -> tuple[str, str]:
    """Returns (browser_name, device_type) from the User-Agent string."""
    ua = user_agent.lower()
    device_type = "desktop"
    if any(x in ua for x in ["mobile", "android", "iphone", "ipad"]):
        device_type = "mobile" if "ipad" not in ua else "tablet"

    if "edg/" in ua:
        browser = "Microsoft Edge"
    elif "chrome/" in ua and "chromium" not in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "opr/" in ua or "opera" in ua:
        browser = "Opera"
    elif "msie" in ua or "trident/" in ua:
        browser = "Internet Explorer"
    else:
        browser = "Unknown"

    return browser, device_type


def _infer_resource_type(path: str) -> str | None:
    """Infer the resource type from the URL path."""
    segments = [s for s in path.split("/") if s]
    resource_map = {
        "conditions": "medical_condition",
        "medications": "medication",
        "allergies": "allergy",
        "visits": "doctor_visit",
        "vaccinations": "vaccination",
        "vitals": "vitals",
        "appointments": "appointment",
        "emergency": "emergency_contact",
        "documents": "medical_document",
        "auth": "auth",
        "analytics": "analytics",
    }
    for segment in segments:
        if segment in resource_map:
            return resource_map[segment]
    return None


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if any(path.startswith(x) for x in SKIP_PREFIXES):
            return await call_next(request)

        # Generate correlation ID to link events in the same request lifecycle
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Extract context BEFORE response
        ip_address = request.client.host if request.client else "unknown"
        raw_user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        browser, device_type = _parse_browser(raw_user_agent)

        # Execute the request
        response = await call_next(request)

        # Extract context AFTER response
        status_code = response.status_code
        user_id = getattr(request.state, "user_id", None)
        actor_email = getattr(request.state, "actor_email", None)

        action = METHOD_ACTION_MAP.get(method, method)
        resource_type = _infer_resource_type(path)

        # Infer resource_id from path (last segment if UUID-shaped)
        path_parts = [s for s in path.split("/") if s]
        resource_id = None
        if path_parts:
            last = path_parts[-1]
            if len(last) == 36 and last.count("-") == 4:
                resource_id = last

        # Build descriptive event_type label: e.g. CREATE_VITALS, READ_APPOINTMENT
        if resource_type:
            event_type = f"{action}_{resource_type.upper()}"
        else:
            event_type = f"{method} {path}"

        # Write to database (non-blocking best-effort)
        db = SessionLocal()
        try:
            audit_entry = AuditLog(
                correlation_id=correlation_id,
                user_id=user_id,
                actor_email=actor_email,
                event_type=event_type,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                endpoint=path,
                http_method=method,
                ip_address=ip_address,
                user_agent=raw_user_agent[:512],
                browser=browser,
                device_type=device_type,
                status_code=status_code,
                details=f"Response: {status_code}",
            )
            db.add(audit_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Audit log write failed: {str(e)}")
        finally:
            db.close()

        return response
