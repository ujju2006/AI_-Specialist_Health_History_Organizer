from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.security.jwt import decode_token
from app.models.models import User
from app.services.auth_service import auth_service

# Defines standard extraction header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency extractor retrieving authenticated User details, appending audits if mapping fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )

    email: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    if email is None or user_id is None:
        raise credentials_exception

    user = auth_service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    # Expose user_id context to HTTP request state for Middleware auditor logging
    request.state.user_id = user.id

    return user

def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    return user

def get_current_doctor(user: User = Depends(get_current_user)) -> User:
    """
    Validates that the authenticated user possesses Doctor or Administrator privileges.
    """
    if user.primary_role not in ("Doctor", "Administrator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires Doctor or Administrator privileges."
        )
    return user

def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """
    Validates that the authenticated user possesses Administrator privileges.
    """
    if user.primary_role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires Administrator privileges."
        )
    return user
