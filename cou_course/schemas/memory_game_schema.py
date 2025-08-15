from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryGameBase(BaseModel):
    course_id: int
    topic_id: int
    description: str = Field(..., min_length=1)
    is_completed: Optional[bool] = False
    active: Optional[bool] = True

class MemoryGameCreate(MemoryGameBase):
    created_by: int

class MemoryGameUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    is_completed: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class MemoryGameRead(MemoryGameBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 