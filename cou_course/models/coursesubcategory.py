# cou_admin/models/country.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class CourseSubcategory(SQLModel, table=True):
    __tablename__ = "course_subcategory"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="cou_course.coursecategory.id")
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_flagship: Optional[bool] = Field(default=False)
    active: Optional[bool] = Field(default=True)