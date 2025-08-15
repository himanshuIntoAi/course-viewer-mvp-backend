from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import JSON, Column

if TYPE_CHECKING:
    from cou_course.models.course import Course
    from cou_course.models.topic import Topic

class Mindmap(SQLModel, table=True):
    __tablename__ = "mindmap"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="cou_course.course.id")
    topic_id: int = Field(foreign_key="cou_course.topic.id")
    mindmap_mermaid: Optional[str] = None
    mindmap_json: Optional[str] = Field(default=None, sa_column=Column(JSON))
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="mindmaps")
    topic: Optional["Topic"] = Relationship(back_populates="mindmaps") 