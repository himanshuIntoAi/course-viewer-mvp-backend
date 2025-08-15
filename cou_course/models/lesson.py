from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic

class Lesson(SQLModel, table=True):
    __tablename__ = "lesson"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    course_id: int = Field(foreign_key="cou_course.course.id")
    title: str = Field(max_length=500)
    content: Optional[str] = None
    video_source: Optional[str] = None
    video_path: Optional[str] = None
    video_filename: Optional[str] = None
    image_path: Optional[str] = None
    is_completed: bool = Field(default=False)
    code: Optional[str] = None  # Code snippet for the lesson
    code_language: Optional[str] = None  # Programming language for the code
    code_output: Optional[str] = None  # Expected output of the code
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    topic: Optional["Topic"] = Relationship(back_populates="lessons")
    course: Optional["Course"] = Relationship(back_populates="lessons") 