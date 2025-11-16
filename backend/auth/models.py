"""
Authentication models and schemas
Pydantic models for user registration and login
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    name: Optional[str] = None

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

