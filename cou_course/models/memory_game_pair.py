from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from cou_course.models.memory_game import MemoryGame

class MemoryGamePair(SQLModel, table=True):
    __tablename__ = "memory_game_pair"
    __table_args__ = {"schema": "cou_course"}

    id: Optional[int] = Field(default=None, primary_key=True)
    memory_game_id: int = Field(foreign_key="cou_course.memory_game.id")
    term: str
    term_description: str
    pair_order: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[int] = None
    active: bool = Field(default=True)

    # Relationships
    memory_game: Optional["MemoryGame"] = Relationship(back_populates="memory_game_pairs") 