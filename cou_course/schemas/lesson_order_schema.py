from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# Define valid component types
ComponentType = Literal['flashcards', 'mindmap', 'quiz', 'memory_game']

class LessonOrderBase(BaseModel):
    course_id: int
    topic_id: int
    component_type: ComponentType
    lesson_ref_id: int
    sort_order: Optional[int] = None
    active: Optional[bool] = True

class LessonOrderCreate(LessonOrderBase):
    created_by: int

class LessonOrderUpdate(BaseModel):
    component_type: Optional[ComponentType] = None
    lesson_ref_id: Optional[int] = None
    sort_order: Optional[int] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class LessonOrderRead(LessonOrderBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 