"""
Admin Governance Portal Router
==============================
Provides enterprise governance endpoints for Administrators to manage users,
assign roles, monitor active sessions, review audit logs, and track security events.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.models import User, Role, AuditLog, UserSession, SecurityEvent
from app.schemas.schemas import AdminUserListItem, AuditLogResponse, SecurityEventResponse
from app.routers.deps import get_current_admin
from app.repositories.repositories import user_repo, role_repo, audit_repo, session_repo, security_event_repo

router = APIRouter(prefix="/admin", tags=["Admin Governance Portal"])


@router.get("/users", response_model=List[AdminUserListItem])
def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Lists all platform users with account status, login attempts, and assigned roles.
    """
    query = db.query(User).filter(User.is_deleted == False)
    users = query.offset(skip).limit(limit).all()

    items = []
    for u in users:
        role_name = u.primary_role
        if role_filter and role_filter.lower() != role_name.lower():
            continue
        items.append(AdminUserListItem(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            role=role_name,
            is_active=u.is_active,
            is_verified=u.is_verified,
            created_at=u.created_at,
            login_attempts=u.login_attempts
        ))
    return items


@router.put("/user/{user_id}/role")
def assign_user_role(
    user_id: str,
    role_name: str = Query(..., description="Target role: Patient, Doctor, or Administrator"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Assigns or updates a user's primary role in the enterprise platform.
    """
    target_user = user_repo.get(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    role = role_repo.get_by_name(db, role_name)
    if not role:
        # Create role if missing in current DB schema
        role = role_repo.create(db, {"name": role_name, "description": f"{role_name} privileges"})

    target_user.roles = [role]
    if hasattr(target_user, "version"):
        target_user.version = (target_user.version or 1) + 1

    db.add(target_user)
    db.commit()
    db.refresh(target_user)

    # Log audit
    audit_repo.create(db, {
        "user_id": current_admin.id,
        "actor_email": current_admin.email,
        "event_type": "ROLE_ASSIGNMENT",
        "action": "UPDATE",
        "resource_type": "UserRole",
        "resource_id": target_user.id,
        "new_value": f"Assigned role: {role_name}",
        "details": f"Admin {current_admin.email} assigned role '{role_name}' to user {target_user.email}."
    })

    return {"status": "success", "user_id": target_user.id, "email": target_user.email, "new_role": role_name}


@router.put("/user/{user_id}/status")
def toggle_user_status(
    user_id: str,
    is_active: bool = Query(..., description="True to activate, False to suspend"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Suspends or reactivates a user account.
    """
    target_user = user_repo.get(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.is_active = is_active
    if hasattr(target_user, "version"):
        target_user.version = (target_user.version or 1) + 1

    db.add(target_user)
    db.commit()
    return {"status": "success", "user_id": target_user.id, "is_active": target_user.is_active}


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_system_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Retrieves immutable system audit trail with filtering support.
    """
    query = db.query(AuditLog)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    return query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()


@router.get("/sessions")
def list_active_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Lists active device sessions across the entire platform.
    """
    sessions = db.query(UserSession).filter(UserSession.is_active == True).order_by(desc(UserSession.last_used_at)).offset(skip).limit(limit).all()
    res = []
    for s in sessions:
        u = user_repo.get(db, s.user_id)
        res.append({
            "id": s.id,
            "user_id": s.user_id,
            "user_email": u.email if u else "Unknown",
            "device_info": s.device_info or "Standard Browser / OS",
            "ip_address": s.ip_address or "127.0.0.1",
            "created_at": s.created_at.isoformat() if s.created_at else "N/A",
            "last_used_at": s.last_used_at.isoformat() if s.last_used_at else "N/A",
            "expires_at": s.expires_at.isoformat() if s.expires_at else "N/A"
        })
    return res


@router.delete("/session/{session_id}")
def force_revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Forcefully terminates an active user device session.
    """
    s = session_repo.get(db, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found.")
    s.is_active = False
    db.add(s)
    db.commit()
    return {"status": "revoked", "session_id": session_id}


@router.get("/security-events", response_model=List[SecurityEventResponse])
def get_security_metrics(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Retrieves recent security alerts, failed login attempts, and account lockouts.
    """
    return security_event_repo.get_recent_events(db, limit)


@router.get("/metrics")
def get_system_overview_metrics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Returns basic application metrics (presented as application statistics, not full observability).
    """
    total_users = db.query(User).filter(User.is_deleted == False).count()
    active_sessions = db.query(UserSession).filter(UserSession.is_active == True).count()
    total_audits = db.query(AuditLog).count()
    recent_security = db.query(SecurityEvent).count()

    return {
        "platform_status": "Healthy",
        "total_active_accounts": total_users,
        "current_active_sessions": active_sessions,
        "audit_trail_records": total_audits,
        "security_events_logged": recent_security,
        "environment": "Production SaaS Platform"
    }
