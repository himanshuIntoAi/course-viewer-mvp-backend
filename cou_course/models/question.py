from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, Dict, Any, Union, List
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import JSON, Column

if TYPE_CHECKING:
    from cou_course.models.quiz import Quiz

class QuestionType(str, Enum):
    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"
    MATCHING_TEXT = "MATCHING_TEXT"
    MATCHING_IMAGE = "MATCHING_IMAGE"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"
    OPEN_ENDED = "OPEN_ENDED"
    SORT_ANSWER = "SORT_ANSWER"

class Question(SQLModel, table=True):
    __tablename__ = "question"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="cou_course.quiz.id")
    type: QuestionType = Field(default=QuestionType.SINGLE)
    question_text: str
    points: int = Field(default=1)
    answers: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(default=None, sa_column=Column(JSON))
    question_order: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    quiz: Optional["Quiz"] = Relationship(back_populates="questions") 