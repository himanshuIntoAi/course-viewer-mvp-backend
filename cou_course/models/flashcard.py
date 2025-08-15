from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic

class Flashcard(SQLModel, table=True):
    __tablename__ = "flashcard"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="cou_course.course.id")
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    flashcard_set_id: int  # Reference to flashcard set
    front: str
    back: str
    clue: Optional[str] = None
    card_order: Optional[int] = None
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="flashcards")
    topic: Optional["Topic"] = Relationship(back_populates="flashcards") 