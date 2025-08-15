from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TopicBase(BaseModel):
    course_id: int
    title: str = Field(..., min_length=1, max_length=500)
    topic_order: Optional[int] = None
    image_path: Optional[str] = None
    is_expanded: Optional[bool] = False
    active: Optional[bool] = True

class TopicCreate(TopicBase):
    created_by: int

class TopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    topic_order: Optional[int] = None
    image_path: Optional[str] = None
    is_expanded: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class TopicRead(TopicBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 