from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class LessonBase(BaseModel):
    topic_id: int
    course_id: int
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    video_source: Optional[str] = None
    video_path: Optional[str] = None
    video_filename: Optional[str] = None
    image_path: Optional[str] = None
    is_completed: Optional[bool] = False
    active: Optional[bool] = True
    code: Optional[str] = None  # Code snippet for the lesson
    code_language: Optional[str] = None  # Programming language for the code
    code_output: Optional[str] = None  # Expected output of the code

class LessonCreate(LessonBase):
    created_by: int

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    video_source: Optional[str] = None
    video_path: Optional[str] = None
    video_filename: Optional[str] = None
    image_path: Optional[str] = None
    is_completed: Optional[bool] = None
    active: Optional[bool] = None
    code: Optional[str] = None  # Code snippet for the lesson
    code_language: Optional[str] = None  # Programming language for the code
    code_output: Optional[str] = None  # Expected output of the code
    updated_by: Optional[int] = None

class LessonRead(LessonBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True

class LessonWithCourseInfo(BaseModel):
    # Lesson information
    id: int
    topic_id: int
    course_id: int
    title: str
    content: Optional[str] = None
    video_source: Optional[str] = None
    video_path: Optional[str] = None
    video_filename: Optional[str] = None
    image_path: Optional[str] = None
    is_completed: Optional[bool] = False
    active: Optional[bool] = True
    code: Optional[str] = None  # Code snippet for the lesson
    code_language: Optional[str] = None  # Programming language for the code
    code_output: Optional[str] = None  # Expected output of the code
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None
    
    # Course information
    course_code: Optional[str] = None
    course_code_language: Optional[str] = None

    class Config:
        orm_mode = True 