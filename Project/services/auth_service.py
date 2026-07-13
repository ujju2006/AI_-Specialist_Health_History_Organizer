"""
Auth Service
============
Handles: user registration, authentication, profile management,
password changes, password history enforcement,
session management (device tracking + refresh token rotation).

Security Enhancements:
- Password history: prevents reuse of the last 5 passwords
- Password strength validation (min 8 chars, upper+lower+digit+special)
- Refresh token rotation: each refresh issues a new token and voids the old one
- Device/session management: active sessions tracked per user
"""
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import User, NotificationPreference, Role, PasswordHistory, UserSession
from app.schemas.schemas import UserCreate, UserUpdate, ChangePassword
from app.security.password import hash_password, verify_password
from app.repositories.repositories import user_repo, pref_repo, role_repo

LOCKOUT_LIMIT = 5
LOCKOUT_MINUTES = 15
PASSWORD_HISTORY_LIMIT = 5  # Prevent reuse of last 5 passwords

# Password strength regex: min 8 chars, uppercase, lowercase, digit, special char
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]).{8,}$'
)


def _hash_token(token: str) -> str:
    """SHA-256 hash a refresh token for safe storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def _validate_password_strength(password: str) -> None:
    """Raises ValueError if password does not meet strength requirements."""
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Password must be at least 8 characters and include an uppercase letter, "
            "a lowercase letter, a digit, and a special character (!@#$%^&*...)."
        )


class AuthService:
    def register_user(self, db: Session, user_in: UserCreate) -> User:
        """
        Creates a new user profile with password hashes and initiates preferences.
        Enforces password strength policy on registration.
        """
        email = user_in.email.lower()
        db_user = user_repo.get_by_email(db, email)
        if db_user:
            raise ValueError("Email already registered")

        _validate_password_strength(user_in.password)
        hashed_password = hash_password(user_in.password)

        role_name = getattr(user_in, "role", None)
        if not role_name and getattr(user_in, "roles", None) and len(user_in.roles) > 0:
            role_name = str(user_in.roles[0])
        if not role_name:
            role_name = "user"

        user_data = user_in.model_dump(exclude={"password", "role", "roles"})
        user_data["password_hash"] = hashed_password
        user_data["is_active"] = True
        user_data["is_verified"] = False

        user = user_repo.create(db, user_data)

        # Assign role
        user_role = role_repo.get_by_name(db, role_name)
        if not user_role:
            user_role = role_repo.create(db, {"name": role_name, "description": f"{role_name} Role"})
            if role_name == "user" and not role_repo.get_by_name(db, "admin"):
                role_repo.create(db, {"name": "admin", "description": "System Administrator"})

        user.roles.append(user_role)
        db.commit()
        db.refresh(user)

        # Seed password history with the initial hash
        db.add(PasswordHistory(user_id=user.id, password_hash=hashed_password))
        db.commit()

        # Create notification preferences
        pref_repo.create(db, {
            "user_id": user.id,
            "email_enabled": True,
            "appointment_reminders": True,
            "medication_reminders": True,
            "vaccination_reminders": True,
            "annual_checkup_reminders": True,
        })

        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        """
        Validates login credentials, handles account lockout, resets attempt counter.
        """
        user = user_repo.get_by_email(db, email)
        if not user:
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        if user.locked_until and user.locked_until > datetime.utcnow():
            remain = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            raise ValueError(f"Account locked. Try again in {max(1, remain)} minute(s).")

        if not verify_password(password, user.password_hash):
            user.login_attempts += 1
            if user.login_attempts >= LOCKOUT_LIMIT:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                db.commit()
                raise ValueError(f"Account locked due to consecutive failures. Try again in {LOCKOUT_MINUTES} minutes.")
            db.commit()
            raise ValueError("Invalid email or password")

        user.login_attempts = 0
        user.locked_until = None
        db.commit()
        return user

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return user_repo.get(db, user_id)

    def update_profile(self, db: Session, user_id: str, profile_in: UserUpdate) -> User:
        user = user_repo.get(db, user_id)
        if not user:
            raise ValueError("User not found")
        update_data = profile_in.model_dump(exclude_unset=True)
        return user_repo.update(db, user, update_data)

    def change_password(self, db: Session, user_id: str, change_in: ChangePassword) -> User:
        """
        Changes user password with:
        - Current password verification
        - Password strength validation
        - Password history check (last 5 passwords)
        """
        user = user_repo.get(db, user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(change_in.current_password, user.password_hash):
            raise ValueError("Incorrect current password")

        _validate_password_strength(change_in.new_password)

        # Check against password history
        history = (
            db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(PASSWORD_HISTORY_LIMIT)
            .all()
        )
        for past in history:
            if verify_password(change_in.new_password, past.password_hash):
                raise ValueError(f"You cannot reuse any of your last {PASSWORD_HISTORY_LIMIT} passwords.")

        new_hash = hash_password(change_in.new_password)
        user.password_hash = new_hash
        db.add(PasswordHistory(user_id=user_id, password_hash=new_hash))
        db.commit()
        return user

    # ── Session Management (Refresh Token Rotation) ────────────────────────

    def create_session(
        self,
        db: Session,
        user_id: str,
        refresh_token: str,
        device_info: str,
        ip_address: str,
        expires_at: datetime,
    ) -> UserSession:
        """Stores a new session record (hashed refresh token) for this device."""
        token_hash = _hash_token(refresh_token)
        session = UserSession(
            user_id=user_id,
            refresh_token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def validate_and_rotate_session(
        self,
        db: Session,
        old_refresh_token: str,
        new_refresh_token: str,
    ) -> Optional[UserSession]:
        """
        Validates the old refresh token, deactivates it, and stores the new one.
        Returns the updated session, or None if the token is invalid/expired.
        """
        old_hash = _hash_token(old_refresh_token)
        session = (
            db.query(UserSession)
            .filter(
                UserSession.refresh_token_hash == old_hash,
                UserSession.is_active == True,
            )
            .first()
        )
        if not session or session.expires_at < datetime.utcnow():
            return None

        # Rotate: deactivate old, create new token hash in same session row
        session.refresh_token_hash = _hash_token(new_refresh_token)
        session.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    def revoke_session(self, db: Session, refresh_token: str) -> bool:
        """Deactivates a specific session (logout from one device)."""
        token_hash = _hash_token(refresh_token)
        session = db.query(UserSession).filter(
            UserSession.refresh_token_hash == token_hash
        ).first()
        if not session:
            return False
        session.is_active = False
        db.commit()
        return True

    def revoke_all_sessions(self, db: Session, user_id: str) -> int:
        """Deactivates all sessions for a user (logout everywhere)."""
        updated = (
            db.query(UserSession)
            .filter(UserSession.user_id == user_id, UserSession.is_active == True)
            .all()
        )
        for s in updated:
            s.is_active = False
        db.commit()
        return len(updated)

    def get_active_sessions(self, db: Session, user_id: str):
        """Returns all active sessions for the security dashboard."""
        return (
            db.query(UserSession)
            .filter(UserSession.user_id == user_id, UserSession.is_active == True)
            .order_by(UserSession.last_used_at.desc())
            .all()
        )

    def delete_account(self, db: Session, user_id: str, password: str) -> None:
        """
        Right-to-delete: marks account for deletion after verifying credentials.
        Records deletion request timestamp (data retention policy hook).
        Cascade deletes all records on DB level via relationship cascade rules.
        """
        user = user_repo.get(db, user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(password, user.password_hash):
            raise ValueError("Incorrect password")

        user.deletion_requested_at = datetime.utcnow()
        user.is_active = False
        db.commit()


auth_service = AuthService()
