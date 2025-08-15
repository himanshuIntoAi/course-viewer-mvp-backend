from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class InstructorInfo(BaseModel):
    id: int
    display_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    
    class Config:
        orm_mode = True

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
    price: Optional[float] = 0
    ratings: Optional[float] = 0.0
    IT: Optional[bool] = False
    Coding_Required: Optional[bool] = False
    Avg_Completion_Time: Optional[int] = None
    Course_level: Optional[str] = None
    
class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    instructor: Optional[InstructorInfo]

    class Config:
        orm_mode = True
