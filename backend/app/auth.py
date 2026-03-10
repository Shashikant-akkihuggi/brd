from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import secrets

# Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
security = HTTPBearer()

# ============================================================================
# RBAC Configuration
# ============================================================================

class UserRole:
    """User roles for RBAC system."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    
    @classmethod
    def all_roles(cls) -> List[str]:
        """Get all available roles."""
        return [cls.ADMIN, cls.EDITOR, cls.VIEWER]
    
    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if a role is valid."""
        return role in cls.all_roles()

# Role hierarchy: higher roles inherit permissions from lower roles
ROLE_HIERARCHY = {
    "admin": ["admin", "editor", "viewer"],
    "editor": ["editor", "viewer"],
    "viewer": ["viewer"]
}

def has_permission(user_role: str, required_roles: List[str]) -> bool:
    """
    Check if user role has permission based on required roles.
    Uses role hierarchy for permission inheritance.
    """
    if not user_role or user_role not in ROLE_HIERARCHY:
        return False
    
    user_permissions = ROLE_HIERARCHY[user_role]
    return any(role in user_permissions for role in required_roles)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Truncate password if too long for bcrypt (72 byte limit)
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    # Bcrypt has a 72 byte limit, truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    Default expiry: 15 minutes
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    """
    Create a secure random refresh token.
    This is stored in the database, not a JWT.
    """
    return secrets.token_urlsafe(32)

def create_token_pair(user_id: int, email: str, role: str = "admin") -> dict:
    """Create both access and refresh tokens with role information."""
    access_token = create_access_token(
        data={"sub": str(user_id), "email": email, "role": role}
    )
    refresh_token = create_refresh_token()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate an access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            return None
            
        return payload
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to get current active user.
    Can be extended to check user.is_active from database.
    """
    return current_user

def store_refresh_token(db: Session, user_id: int, refresh_token: str) -> None:
    """Store refresh token in database."""
    from app.models import RefreshToken
    
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=expires_at,
        is_revoked=False
    )
    
    db.add(db_token)
    db.commit()

def verify_refresh_token(db: Session, refresh_token: str) -> Optional[int]:
    """
    Verify refresh token and return user_id if valid.
    Returns None if token is invalid, expired, or revoked.
    """
    from app.models import RefreshToken
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()
    
    if not db_token:
        return None
    
    # Check if revoked
    if db_token.is_revoked:
        return None
    
    # Check if expired
    if db_token.expires_at < datetime.utcnow():
        return None
    
    return db_token.user_id

def revoke_refresh_token(db: Session, refresh_token: str) -> bool:
    """
    Revoke a refresh token (logout).
    Returns True if token was found and revoked.
    """
    from app.models import RefreshToken
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()
    
    if not db_token:
        return False
    
    db_token.is_revoked = True
    db.commit()
    return True

def revoke_all_user_tokens(db: Session, user_id: int) -> int:
    """
    Revoke all refresh tokens for a user (logout from all devices).
    Returns number of tokens revoked.
    """
    from app.models import RefreshToken
    
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    
    db.commit()
    return count

def cleanup_expired_tokens(db: Session) -> int:
    """
    Delete expired refresh tokens from database.
    Should be run periodically (e.g., daily cron job).
    Returns number of tokens deleted.
    """
    from app.models import RefreshToken
    
    count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    
    db.commit()
    return count


# ============================================================================
# RBAC Dependencies
# ============================================================================

async def get_current_user_with_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current user with role information from token.
    Returns dict with user_id, email, and role.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure role exists in payload (default to viewer for old tokens)
    if "role" not in payload:
        payload["role"] = "viewer"
    
    return payload

def require_role(allowed_roles: List[str]):
    """
    Dependency factory to check if user has required role.
    
    Usage:
        @router.delete("/project/{id}")
        def delete_project(
            current_user: dict = Depends(require_role(["admin"]))
        ):
            # Only admins can access this
    
    Args:
        allowed_roles: List of roles that can access the endpoint
    
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        # Get user with role
        user = await get_current_user_with_role(credentials)
        user_role = user.get("role", "viewer")
        
        # Check permission using role hierarchy
        if not has_permission(user_role, allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}. Your role: {user_role}"
            )
        
        return user
    
    return role_checker

def require_admin():
    """Shortcut dependency for admin-only endpoints."""
    return require_role(["admin"])

def require_editor():
    """Shortcut dependency for editor and admin endpoints."""
    return require_role(["admin", "editor"])

def require_viewer():
    """Shortcut dependency for all authenticated users (viewer, editor, admin)."""
    return require_role(["admin", "editor", "viewer"])



# ============================================================================
# Project Ownership Helpers
# ============================================================================

def verify_project_ownership(project, user_id: int) -> bool:
    """
    Verify that the user owns the project.
    
    Args:
        project: Project object from database
        user_id: Current user's ID
    
    Returns:
        True if user owns the project, False otherwise
    """
    if project is None:
        return False
    return project.owner_id == user_id

def get_user_project(db: Session, project_id: int, user_id: int):
    """
    Get a project only if the user owns it.
    
    Args:
        db: Database session
        project_id: Project ID to fetch
        user_id: Current user's ID
    
    Returns:
        Project object if found and owned by user, None otherwise
    """
    from app.models import Project
    return db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id
    ).first()

def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Get all projects owned by a user.
    
    Args:
        db: Database session
        user_id: Current user's ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        List of Project objects owned by the user
    """
    from app.models import Project
    return db.query(Project).filter(
        Project.owner_id == user_id
    ).offset(skip).limit(limit).all()
