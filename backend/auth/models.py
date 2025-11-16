"""
Authentication models and schemas
Pydantic models for user registration and login
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import warnings

class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """
        Validate password length
        Bcrypt has a 72-byte limit, so passwords longer than 72 bytes will be truncated.
        """
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes (will be handled in get_password_hash, but warn user)
            warnings.warn(
                "Password exceeds 72 bytes and will be truncated. "
                "This is a limitation of the bcrypt algorithm.",
                UserWarning
            )
        return v

class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """User response model (without password)"""
    id: int
    email: str
    name: Optional[str] = None


