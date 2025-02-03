from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class MentorBase(BaseModel):
    user_id: int
    bio: Optional[str] = None
    expertise: Optional[str] = None
    rating: Optional[float] = 0.0
    total_students: Optional[int] = 0
    is_available: Optional[bool] = True

class MentorCreate(MentorBase):
    pass

class MentorUpdate(BaseModel):
    bio: Optional[str] = None
    expertise: Optional[str] = None
    rating: Optional[float] = None
    total_students: Optional[int] = None
    is_available: Optional[bool] = None
    
class MentorRead(MentorBase):
    id: int
    user_id: int
    bio: Optional[str] = None
    expertise: Optional[str] = None  # Include this field
    rating: Optional[float] = 0.0
    is_available: Optional[bool] = True  # Include this field
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True