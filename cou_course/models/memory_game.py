from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic
    from cou_course.models.memory_game_pair import MemoryGamePair

class MemoryGame(SQLModel, table=True):
    __tablename__ = "memory_game"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="cou_course.course.id")
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    description: str
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="memory_games")
    topic: Optional["Topic"] = Relationship(back_populates="memory_games")
    memory_game_pairs: List["MemoryGamePair"] = Relationship(back_populates="memory_game") 