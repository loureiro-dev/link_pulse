"""
Admin API routes
Handles user approval, user management, and admin operations
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from backend.auth.middleware import get_current_user
from backend.auth.models import UserResponse
from backend.db.users import (
    list_all_users, approve_user, reject_user, is_admin, get_user_by_id
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin role
    Raises 403 if user is not admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    include_pending: bool = True,
    admin_user: dict = Depends(require_admin)
):
    """
    Get all users (admin only)
    
    Args:
        include_pending: Include pending users (default: True)
        admin_user: Current admin user (from dependency)
        
    Returns:
        List of all users
    """
    users = list_all_users(include_pending=include_pending)
    return [UserResponse(**user) for user in users]


@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(admin_user: dict = Depends(require_admin)):
    """
    Get pending users (admin only)
    
    Args:
        admin_user: Current admin user (from dependency)
        
    Returns:
        List of pending users
    """
    all_users = list_all_users(include_pending=True)
    pending = [u for u in all_users if not u.get("approved", False)]
    return [UserResponse(**user) for user in pending]


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user_endpoint(
    user_id: int,
    admin_user: dict = Depends(require_admin)
):
    """
    Approve a user (admin only)
    
    Args:
        user_id: User ID to approve
        admin_user: Current admin user (from dependency)
        
    Returns:
        Approved user information
        
    Raises:
        HTTPException: If user not found or approval fails
    """
    if not approve_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be approved"
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@router.delete("/users/{user_id}/reject")
async def reject_user_endpoint(
    user_id: int,
    admin_user: dict = Depends(require_admin)
):
    """
    Reject/delete a user (admin only)
    
    Args:
        user_id: User ID to reject/delete
        admin_user: Current admin user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or rejection fails
    """
    if not reject_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be rejected"
        )
    
    return {"message": "User rejected and deleted successfully"}

