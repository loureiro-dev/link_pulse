"""
Profile API routes
Handles user profile updates and password changes
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.auth.middleware import get_current_user
from backend.auth.models import UserResponse, UpdateProfileRequest, ChangePasswordRequest
from backend.db.users import (
    update_user_profile, update_user_password, get_user_by_id, get_user_by_email
)
from backend.auth.jwt import verify_password

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    
    Args:
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Current user information
    """
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    profile_data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user profile
    
    Args:
        profile_data: Profile update data (name, email)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If update fails or email already exists
    """
    user_id = current_user["id"]
    
    success = update_user_profile(
        user_id=user_id,
        name=profile_data.name,
        email=profile_data.email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile. Email may already be in use."
        )
    
    # Get updated user
    updated_user = get_user_by_id(user_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile updated but could not retrieve updated information"
        )
    
    return UserResponse(**updated_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change current user password
    
    Args:
        password_data: Password change data (current_password, new_password)
        current_user: Current authenticated user (from dependency)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If current password is incorrect or update fails
    """
    user_id = current_user["id"]
    
    # Verify current password
    user = get_user_by_email(current_user["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    success = update_user_password(user_id, password_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}

