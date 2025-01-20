from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseCategoryBase(BaseModel):
    name: str
    is_flagship: Optional[bool] = False
    active: Optional[bool] = True

class CourseCategoryCreate(CourseCategoryBase):
    pass

class CourseCategoryRead(CourseCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CourseCategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_flagship: Optional[bool] = None
    active: Optional[bool] = None
    updated_at: Optional[datetime] = datetime.utcnow()
