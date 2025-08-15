from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic
    from cou_course.models.question import Question

class Quiz(SQLModel, table=True):
    __tablename__ = "quiz"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    course_id: int = Field(foreign_key="cou_course.course.id")
    title: str = Field(max_length=500)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    max_questions: Optional[int] = None
    passing_grade_percent: Optional[int] = None
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    topic: Optional["Topic"] = Relationship(back_populates="quizzes")
    course: Optional["Course"] = Relationship(back_populates="quizzes")
    questions: List["Question"] = Relationship(back_populates="quiz") 