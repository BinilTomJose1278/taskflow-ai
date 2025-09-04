"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_superuser: bool
    organization_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
