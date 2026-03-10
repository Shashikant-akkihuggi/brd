from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models import User
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_token_pair,
    store_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    get_current_user,
    create_access_token,
    UserRole,
    require_admin
)

router = APIRouter()

# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None
    role: Optional[str] = "admin"  # Default role changed to admin

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LogoutRequest(BaseModel):
    refresh_token: str

class MessageResponse(BaseModel):
    message: str

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    Returns access token (15 min) and refresh token (7 days).
    Default role is 'admin' unless specified.
    """
    try:
        # Validate role
        if user_data.role and not UserRole.is_valid_role(user_data.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(UserRole.all_roles())}"
            )
        
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create new user with admin role by default
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role or "admin"  # Changed default to admin
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create token pair with role
        tokens = create_token_pair(new_user.id, new_user.email, new_user.role)
        
        # Store refresh token in database
        store_refresh_token(db, new_user.id, tokens["refresh_token"])
        
        return {
            **tokens,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "role": new_user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with username and password.
    Returns access token (15 min) and refresh token (7 days) with role information.
    """
    try:
        # Find user by username
        user = db.query(User).filter(User.username == user_data.username).first()
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create token pair with role
        tokens = create_token_pair(user.id, user.email, user.role)
        
        # Store refresh token in database
        store_refresh_token(db, user.id, tokens["refresh_token"])
        
        return {
            **tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh-token", response_model=AccessTokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest, 
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    Returns new access token (15 min) with role information.
    Refresh token remains valid until expiry.
    """
    try:
        # Verify refresh token
        user_id = verify_refresh_token(db, request.refresh_token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user with role
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token with role
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 15 * 60  # 15 minutes in seconds
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout", response_model=MessageResponse)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token.
    Access token will expire naturally (15 min).
    """
    try:
        success = revoke_refresh_token(db, request.refresh_token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found"
            )
        
        return {"message": "Successfully logged out"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.post("/logout-all", response_model=MessageResponse)
def logout_all_devices(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices by revoking all refresh tokens.
    Requires valid access token.
    """
    try:
        user_id = int(current_user["sub"])
        count = revoke_all_user_tokens(db, user_id)
        
        return {"message": f"Successfully logged out from {count} device(s)"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout all failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Get current user information including role.
    Requires valid access token.
    """
    user = db.query(User).filter(User.id == int(current_user["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    }

class UpdateUserRole(BaseModel):
    user_id: int
    new_role: str

@router.post("/update-role", response_model=MessageResponse)
def update_user_role(
    request: UpdateUserRole,
    current_user: dict = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only).
    Only admins can change user roles.
    """
    try:
        # Validate new role
        if not UserRole.is_valid_role(request.new_role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(UserRole.all_roles())}"
            )
        
        # Find user
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update role
        old_role = user.role
        user.role = request.new_role
        db.commit()
        
        return {
            "message": f"User role updated from '{old_role}' to '{request.new_role}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )
