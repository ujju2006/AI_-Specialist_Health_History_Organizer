from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate, ChangePassword, Token
from app.services.auth_service import auth_service
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.routers.deps import get_current_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new standard user account.
    Enforces password strength policy (uppercase, lowercase, digit, special char, min 8 chars).
    """
    try:
        user = auth_service.register_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates via OAuth2 email/password.
    Issues access + refresh token pair and records a device session.
    """
    try:
        user = auth_service.authenticate_user(db, form_data.username, form_data.password)

        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

        # Record session for device management
        device_info = request.headers.get("user-agent", "unknown")[:255]
        ip_address = request.client.host if request.client else "unknown"
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        auth_service.create_session(db, user.id, refresh_token, device_info, ip_address, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    """
    Validates an existing refresh token, rotates it (issues new pair),
    and invalidates the old session entry (refresh token rotation).
    """
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("user_id")
    user = auth_service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session")

    new_access = create_access_token(data={"sub": user.email, "user_id": user.id})
    new_refresh = create_refresh_token(data={"sub": user.email, "user_id": user.id})

    # Rotate session - swap old token hash for new one
    session = auth_service.validate_and_rotate_session(db, refresh_token, new_refresh)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or revoked")

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Revokes the current device session (logout from this device only).
    """
    auth_service.revoke_session(db, refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Revokes all active sessions for the current user (logout from all devices).
    """
    count = auth_service.revoke_all_sessions(db, current_user.id)
    return {"message": f"Logged out from {count} active session(s)"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(profile_in: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Updates profile fields for the current authenticated user."""
    try:
        user = auth_service.update_profile(db, current_user.id, profile_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/me/password", response_model=UserResponse)
def change_my_password(change_in: ChangePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Changes current user password.
    Enforces: strength validation + password history (last 5 passwords).
    """
    try:
        user = auth_service.change_password(db, current_user.id, change_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me/sessions")
def get_my_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns all active device sessions for the security dashboard.
    Shows: device info, IP address, last used, creation date.
    """
    sessions = auth_service.get_active_sessions(db, current_user.id)
    return [
        {
            "id": s.id,
            "device_info": s.device_info,
            "ip_address": s.ip_address,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "last_used_at": s.last_used_at.isoformat() if s.last_used_at else None,
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
        }
        for s in sessions
    ]


@router.delete("/me/account")
def delete_my_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Privacy compliance: Right-to-delete.
    Deactivates the account and records deletion request timestamp.
    All associated health records are cascade-deleted via DB relationships.
    """
    try:
        auth_service.delete_account(db, current_user.id, password)
        return {"message": "Account deletion initiated. All associated data will be removed per our data retention policy."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
