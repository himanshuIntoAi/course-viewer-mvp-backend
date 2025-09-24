from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_user.models.user import User
    from cou_mentor.models.mentor import Mentor
    from cou_course.models.topic import Topic
    from cou_course.models.lesson import Lesson
    from cou_course.models.quiz import Quiz
    from cou_course.models.mindmap import Mindmap
    from cou_course.models.memory_game import MemoryGame
    from cou_course.models.flashcard import Flashcard
    from cou_course.models.lesson_order import LessonOrder

# Ensure LessonOrder mapper is registered before resolving relationships
from cou_course.models.lesson_order import LessonOrder  # noqa: F401
from cou_mentor.models.mentor import Mentor  # noqa: F401

class Course(SQLModel, table=True):
    __tablename__ = "course"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    what_will_you_learn: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="cou_course.course_category.id")
    subcategory_id: Optional[int] = Field(default=None, foreign_key="cou_course.course_subcategory.id")
    course_type_id: Optional[int] = Field(default=None, foreign_key="cou_course.course_type.id")
    sells_type_id: Optional[int] = Field(default=None, foreign_key="cou_course.sells_type.id")
    language_id: Optional[int] = Field(default=None, foreign_key="cou_admin.language.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_flagship: Optional[bool] = Field(default=False)
    active: Optional[bool] = Field(default=True)
    ratings: Optional[int] = Field(default=0)
    price: Optional[float] = Field(default=0.0)
    mentor_id: Optional[int] = Field(default=None, foreign_key="cou_user.user.id")
    IT: Optional[bool] = Field(default=None, sa_column_kwargs={"name": "IT"})
    Coding_Required: Optional[bool] = Field(default=None, sa_column_kwargs={"name": "Coding_Required"})
    Avg_Completion_Time: Optional[int] = Field(default=None, sa_column_kwargs={"name": "Avg_Completion_TIme"})
    Course_level: Optional[str] = Field(default=None, sa_column_kwargs={"name": "Course_level"})  # "beginner", "intermediate", "advanced"
    # Note: code and code_language fields removed as they don't exist in the database table
    # code: Optional[str] = Field(default=None, max_length=100)  # Course code/identifier
    # code_language: Optional[str] = Field(default=None, max_length=50)  # Programming language for coding courses
    
    # Relationships
    mentor: Optional["Mentor"] = Relationship(
        back_populates="courses",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(Course.mentor_id)==Mentor.user_id",
            "lazy": "selectin"
        }
    )
    topics: List["Topic"] = Relationship(back_populates="course")
    lessons: List["Lesson"] = Relationship(back_populates="course")
    quizzes: List["Quiz"] = Relationship(back_populates="course")
    mindmaps: List["Mindmap"] = Relationship(back_populates="course")
    memory_games: List["MemoryGame"] = Relationship(back_populates="course")
    flashcards: List["Flashcard"] = Relationship(back_populates="course")
    lesson_orders: List["LessonOrder"] = Relationship(back_populates="course")
