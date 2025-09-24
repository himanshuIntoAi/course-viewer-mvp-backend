from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone

class Mentor(SQLModel, table=True):
    __tablename__ = "mentor"
    __table_args__ = {"schema": "cou_mentor"}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="cou_user.user.id", unique=True)
    bio: Optional[str] = None
    expertise: Optional[str] = Field(default=None, max_length=500)
    designation: Optional[str] = Field(default=None, max_length=500)
    # rating column does not exist in DB; removed to match schema
    # is_available column does not exist in DB; removed to match schema
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="mentor")
    courses: List["Course"] = Relationship(
        back_populates="mentor",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Course.mentor_id)==Mentor.user_id",
            "lazy": "selectin"
        }
    )
    
    @property
    def total_students(self) -> int:
        return sum(course.total_enrollments for course in self.courses) if self.courses else 0