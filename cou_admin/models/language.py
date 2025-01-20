# cou_admin/models/country.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Language(SQLModel, table=True):
    __tablename__ = "language"
    __table_args__ = {"schema": "cou_admin"}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    short_name: Optional[str] = Field(default=None, max_length=50)
    country_id: Optional[int] = Field(default=None, foreign_key="cou_admin.country.id")
    state_id: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_flagship: Optional[bool] = Field(default=False)
    active: Optional[bool] = Field(default=True)