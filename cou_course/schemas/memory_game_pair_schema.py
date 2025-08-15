from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryGamePairBase(BaseModel):
    memory_game_id: int
    term: str = Field(..., min_length=1)
    term_description: str = Field(..., min_length=1)
    pair_order: Optional[int] = None
    active: Optional[bool] = True

class MemoryGamePairCreate(MemoryGamePairBase):
    created_by: int

class MemoryGamePairUpdate(BaseModel):
    term: Optional[str] = Field(None, min_length=1)
    term_description: Optional[str] = Field(None, min_length=1)
    pair_order: Optional[int] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class MemoryGamePairRead(MemoryGamePairBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 