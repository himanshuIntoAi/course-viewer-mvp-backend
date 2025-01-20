from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    work_email: Optional[str] = None
    personal_email: Optional[str] = None

class UserCreate(UserBase):
    created_by: int
    role_id: Optional[int] = None

class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    active: Optional[bool] = None
    updated_by: int

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    active: bool
    premium: bool
    facebook: Optional[str]
    instagram: Optional[str]
    linkedin: Optional[str]
    twitter: Optional[str]
    youtube: Optional[str]

    class Config:
        orm_mode = True