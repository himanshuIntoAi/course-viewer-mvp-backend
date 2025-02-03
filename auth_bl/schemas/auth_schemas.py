from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class AuthRequest(BaseModel):
    code: str
    redirect_uri: str
    state: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "auth_code_here",
                "redirect_uri": "http://localhost:3000/callback",
                "state": "optional_state_data"
            }
        }

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str
    email: Optional[str] = None
    profile_image: Optional[str] = None
    expires_in: int = Field(default=86400)  # 1 day in seconds
    redirect_path: Optional[str] = None

    class Config:
        from_attributes = True

class StateData(BaseModel):
    stateId: str
    redirectPath: str
    timestamp: int

class EmailAuthRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secretpassword"
            }
        }

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secretpassword",
                "first_name": "John",
                "last_name": "Doe"
            }
        }

class GoogleAuthRequest(AuthRequest):
    """Google OAuth authentication request schema"""
    pass  # Uses the same fields as base AuthRequest