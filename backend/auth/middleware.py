"""
Authentication middleware and dependencies
Protects routes by validating JWT tokens
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.auth.jwt import decode_access_token
from backend.db.users import get_user_by_id, get_user_by_email

security = HTTPBearer()


async def get_current_user_from_token(token: str) -> dict:
    """
    Extract and validate user from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User dict with id, email, name
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info from token
    user_email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    
    if user_email is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database (always get fresh data, including is_admin)
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Always use is_admin from database (more reliable than token)
    # Token may be outdated if user was promoted to admin after login
    # Database is the source of truth
    # Ensure is_admin is always a boolean
    user["is_admin"] = bool(user.get("is_admin", False))
    user["approved"] = bool(user.get("approved", False))
    
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency to get current authenticated user
    Use this in route dependencies to protect endpoints
    
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"user": current_user}
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User dict with id, email, name
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    return await get_current_user_from_token(credentials.credentials)


# Optional: Create a dependency that makes auth optional (for gradual migration)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optional authentication dependency
    Returns user if token is valid, None otherwise (no exception)
    Useful for endpoints that work with or without auth
    
    Args:
        credentials: Optional HTTP Bearer token
        
    Returns:
        User dict if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user_from_token(credentials.credentials)
    except HTTPException:
        return None


