from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int]
    subcategory_id: Optional[int]
    course_type_id: Optional[int]
    sells_type_id: Optional[int]
    mentor_id: Optional[int]
    language_id: Optional[int]
    is_flagship: Optional[bool] = False
    active: Optional[bool] = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    mentor: Optional[int]

    class Config:
        orm_mode = True
