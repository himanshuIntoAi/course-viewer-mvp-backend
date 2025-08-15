from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Video-related schemas (from existing file)
class VideoInfo(BaseModel):
    name: str
    url: str
    content_type: str
    size: int

class VideoListResponse(BaseModel):
    videos: List[VideoInfo]

# Additional learning content schemas
class LearningContentSummary(BaseModel):
    total_lessons: int
    total_quizzes: int
    total_flashcards: int
    total_mindmaps: int
    total_memory_games: int
    total_topics: int

class CourseLearningContent(BaseModel):
    course_id: int
    course_title: str
    code: Optional[str] = None  # Course code/identifier
    code_language: Optional[str] = None  # Programming language for coding courses
    learning_content: Dict[str, Any]
    content_summary: LearningContentSummary

# Flashcard set schema (since flashcards are organized in sets)
class FlashcardSetBase(BaseModel):
    course_id: int
    topic_id: int
    title: str
    description: Optional[str] = None
    active: bool = True

class FlashcardSetCreate(FlashcardSetBase):
    created_by: int

class FlashcardSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class FlashcardSetRead(FlashcardSetBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True

# Course progress tracking schema
class CourseProgressBase(BaseModel):
    course_id: int
    user_id: int
    completed_lessons: int = 0
    completed_quizzes: int = 0
    completed_flashcards: int = 0
    completed_mindmaps: int = 0
    completed_memory_games: int = 0
    overall_progress_percentage: float = 0.0
    last_accessed_at: Optional[datetime] = None

class CourseProgressCreate(CourseProgressBase):
    pass

class CourseProgressUpdate(BaseModel):
    completed_lessons: Optional[int] = None
    completed_quizzes: Optional[int] = None
    completed_flashcards: Optional[int] = None
    completed_mindmaps: Optional[int] = None
    completed_memory_games: Optional[int] = None
    overall_progress_percentage: Optional[float] = None
    last_accessed_at: Optional[datetime] = None

class CourseProgressRead(CourseProgressBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
