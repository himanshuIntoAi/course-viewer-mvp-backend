from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from pydantic import BaseModel, Field
from cou_course.models.question import QuestionType

class QuestionBase(BaseModel):
    quiz_id: int
    type: QuestionType = QuestionType.SINGLE
    question_text: str = Field(..., min_length=1)
    points: int = Field(default=1, ge=1)
    answers: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None  # JSONB field for flexible answer structure
    question_order: Optional[int] = None
    active: Optional[bool] = True

class QuestionCreate(QuestionBase):
    created_by: int

class QuestionUpdate(BaseModel):
    type: Optional[QuestionType] = None
    question_text: Optional[str] = Field(None, min_length=1)
    points: Optional[int] = Field(None, ge=1)
    answers: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    question_order: Optional[int] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class QuestionRead(QuestionBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True 