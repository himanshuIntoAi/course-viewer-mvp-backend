# cou_admin/models/country.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone

class Course(SQLModel, table=True):
    __tablename__ = "course"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="cou_course.category.id")
    subcategory_id: Optional[int] = Field(default=None, foreign_key="cou_course.subcategory.id")
    course_type_id: Optional[int] = Field(default=None, foreign_key="cou_course.coursetype.id")
    sells_type_id: Optional[int] = Field(default=None, foreign_key="cou_course.sellstype.id")
    mentor_id: Optional[int] = Field(default=None, foreign_key="cou_user.user.id")
    language_id: Optional[int] = Field(default=None, foreign_key="cou_admin.language.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    total_enrollments: Optional[int] = Field(default=0)
    is_flagship: Optional[bool] = Field(default=False)
    active: Optional[bool] = Field(default=True)
    mentor_id: Optional[int] = Field(default=None, foreign_key="cou_user.mentor.id")
    mentor: Optional["Mentor"] = Relationship(back_populates="courses")