from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone


# Login Type Model
class LoginType(SQLModel, table=True):
    __tablename__ = "login_type"
    __table_args__ = {"schema": "cou_user"}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False)
    details: Optional[str] = Field(max_length=100, default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int = Field(nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: int = Field(nullable=False)
    active: Optional[bool] = Field(default=True)
    auth_type: Optional[str] = Field(max_length=50, default=None)