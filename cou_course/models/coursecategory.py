from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class CourseCategory(SQLModel, table=True):
    __tablename__ = "course_category"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_flagship: bool = Field(default=False)
    active: bool = Field(default=True)
