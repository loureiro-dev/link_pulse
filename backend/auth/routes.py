"""
Authentication routes
Handles user registration and login endpoints
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.models import UserRegister, UserLogin, TokenResponse, UserResponse
from backend.auth.jwt import create_access_token
from backend.db.users import create_user, authenticate_user, get_user_by_id
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    Args:
        user_data: User registration data (email, password, optional name)
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException: If email already exists or registration fails
    """
    success, user_id, error_message = create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Registration failed"
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User created but could not be retrieved"
        )
    
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Login user and return JWT token
    
    Args:
        user_data: User login data (email, password)
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid or user not approved
    """
    user = authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is approved (admins can always login)
    if not user.get("approved", False) and not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval. Please wait for an administrator to approve your account.",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"], "is_admin": user.get("is_admin", False)},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """
    Get current authenticated user information
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from backend.auth.middleware import get_current_user_from_token
    try:
        user = await get_current_user_from_token(credentials.credentials)
        # Ensure all required fields are present with defaults
        user_data = {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "is_admin": bool(user.get("is_admin", False)),
            "approved": bool(user.get("approved", False))
        }
        return UserResponse(**user_data)
    except Exception as e:
        import traceback
        print(f"Error in /auth/me: {e}")
        traceback.print_exc()
        raise


