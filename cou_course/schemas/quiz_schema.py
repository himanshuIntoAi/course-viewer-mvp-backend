from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class QuizBase(BaseModel):
    topic_id: int
    course_id: int
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    max_questions: Optional[int] = Field(None, ge=1)
    passing_grade_percent: Optional[int] = Field(None, ge=0, le=100)
    is_completed: Optional[bool] = False
    active: Optional[bool] = True

class QuizCreate(QuizBase):
    created_by: int

class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    max_questions: Optional[int] = Field(None, ge=1)
    passing_grade_percent: Optional[int] = Field(None, ge=0, le=100)
    is_completed: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class QuizRead(QuizBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 