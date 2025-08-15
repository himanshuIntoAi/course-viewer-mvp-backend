from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic

class ComponentType(str, Enum):
    FLASHCARDS = "flashcards"
    MINDMAP = "mindmap"
    QUIZ = "quiz"
    MEMORY_GAME = "memory_game"

class LessonOrder(SQLModel, table=True):
    __tablename__ = "LessonOrder"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="cou_course.course.id")
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    component_type: ComponentType
    lesson_ref_id: int
    sort_order: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="lesson_orders")
    topic: Optional["Topic"] = Relationship(back_populates="lesson_orders") 