from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FlashcardBase(BaseModel):
    course_id: int
    topic_id: int
    flashcard_set_id: int
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)
    clue: Optional[str] = None
    card_order: Optional[int] = None
    is_completed: Optional[bool] = False
    active: Optional[bool] = True

class FlashcardCreate(FlashcardBase):
    created_by: int

class FlashcardUpdate(BaseModel):
    front: Optional[str] = Field(None, min_length=1)
    back: Optional[str] = Field(None, min_length=1)
    clue: Optional[str] = None
    card_order: Optional[int] = None
    is_completed: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class FlashcardRead(FlashcardBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 