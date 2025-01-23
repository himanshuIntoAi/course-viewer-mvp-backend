from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone

class Role(SQLModel, table=True):
    __tablename__ = "role"
    __table_args__ = {"schema": "cou_user"}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: int
    active: Optional[bool] = Field(default=True)