from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.lesson import Lesson
    from cou_course.models.quiz import Quiz
    from cou_course.models.mindmap import Mindmap
    from cou_course.models.memory_game import MemoryGame
    from cou_course.models.flashcard import Flashcard

class Topic(SQLModel, table=True):
    __tablename__ = "topic"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="cou_course.course.id")
    title: str = Field(max_length=500)
    topic_order: Optional[int] = None
    image_path: Optional[str] = None
    is_expanded: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="topics")
    lessons: List["Lesson"] = Relationship(back_populates="topic")
    quizzes: List["Quiz"] = Relationship(back_populates="topic")
    mindmaps: List["Mindmap"] = Relationship(back_populates="topic")
    memory_games: List["MemoryGame"] = Relationship(back_populates="topic")
    flashcards: List["Flashcard"] = Relationship(back_populates="topic")
    lesson_orders: List["LessonOrder"] = Relationship(back_populates="topic") 