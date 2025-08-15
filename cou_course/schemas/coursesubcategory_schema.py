from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CourseSubcategoryBase(BaseModel):
    name: str
    category_id: int
    is_flagship: Optional[bool] = False
    active: Optional[bool] = True

class CourseSubcategoryCreate(CourseSubcategoryBase):
    created_by: Optional[int] = None

class CourseSubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    is_flagship: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class CourseSubcategoryInDB(CourseSubcategoryBase):
    id: int
    created_at: datetime
    created_by: Optional[int]
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True 